""" Utils Function to implement preprocessing phase """

import os
import cv2
from typing import List, Callable
import numpy as np
import torch
import torchvision
import xml.etree.ElementTree as ET
from utils.Types import Particle


def extract_particles(xml: str) -> List[Particle]:
    """Extract particles detected in xml file

    :param xml: file gth
    :return: list of detected particles
    """
    if not os.path.isfile(xml): return []
    particles = []
    tree = ET.parse(xml)
    root = tree.getroot()
    for i, particle in enumerate(root[0]):
        for detection in particle:
            t, x, y, z = detection.attrib['t'], detection.attrib['x'], detection.attrib['y'], detection.attrib['z']
            particles.append(Particle(int(t), float(x), float(y), float(z)))
    return particles


def query_particles(particles: List[Particle], criteria: Callable[[Particle], int]) -> List[Particle]:
    """Query on given input particles

    :param particles:
    :param criteria:
    :return: particles that respect a certain input criteria
    """
    particles_criteria = [particle for particle in particles if criteria(particle)]
    return particles_criteria


def draw_particles(img_3d: np.ndarray, particles: List[Particle]) -> np.ndarray:
    """Draw particles in 3d image to verify the correctness of particles

    :param img_3d: (H, W, D)
    :param particles:
    :return:
    """
    img = img_3d.copy()
    WHITE = (255, 255, 255) # TODO: perchè 3 canali (rgb)? Non dovrebbe essere tutto monocanale (scala di grigi)?
    for particle in particles:
        x = np.clip(round(particle.x), 0, img_3d.shape[0] - 1)
        y = np.clip(round(particle.y), 0, img_3d.shape[1] - 1)
        z = np.clip(round(particle.z), 0, img_3d.shape[2] - 1)
        _slice = img[:, :, z].astype(np.uint8)
        cv2.circle(_slice, center=(x, y), radius=5, color=WHITE)
        cv2.putText(_slice, text=str(particle.z), org=(x, y), fontFace=cv2.FONT_ITALIC, fontScale=0.4, color=WHITE)
        img[:, :, z] = _slice
    return img


def save_slices(img: torch.Tensor, path: str, img_name: str = None):
    """Save slices as torch grid

    :param img:
    :param path:
    :param img_name:
    :return:
    """
    if img_name is None: img_name = "img.png"
    img = img.squeeze(0)
    img = img.unsqueeze(1)
    img[img != 0] = 255
    img = 1 - img
    os.makedirs(path, exist_ok=True)
    torchvision.utils.save_image(tensor=img, fp=os.path.join(path, img_name), nrow=5, padding=10)
