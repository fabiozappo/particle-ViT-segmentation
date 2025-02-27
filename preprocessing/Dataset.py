"""Define Torch Dataset_original and Dataloader"""
import os
import numpy as np
import cv2
import torch
from typing import Any
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.transforms import functional as F
from utils.definitions import DTS_TRAIN_PATH
from multipledispatch import dispatch
import random


class CustomToTensor(transforms.ToTensor):
    @dispatch(np.ndarray, np.ndarray)
    def __call__(self, img, target) -> Any:
        return F.to_tensor(img), F.to_tensor(target)


class CustomHorizontalFlip(transforms.RandomHorizontalFlip):
    def __call__(self, img, target) -> Any:
        if random.random() < self.p:
            return F.hflip(img), F.hflip(target)
        return img, target


class CustomVerticalFlip(transforms.RandomVerticalFlip):
    def __call__(self, img, target) -> Any:
        if random.random() < self.p:
            return F.vflip(img), F.vflip(target)
        return img, target


class CustomCompose(transforms.Compose):
    @dispatch(np.ndarray, np.ndarray)
    def __call__(self, img, target) -> Any:
        for t in self.transforms:
            img, target = t(img, target)
        return img, target


# dataset
class VirusDataset(Dataset):
    def __init__(self, dir_path: str, transform=None):
        self.dir_path = dir_path
        self.transform = transform
        self.files = os.listdir(self.dir_path)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        data = np.load(os.path.join(self.dir_path, self.files[index]), allow_pickle=True)
        img = np.divide(data['img'], 255.0, dtype=np.float32)
        target = np.divide(data['target'], 255.0, dtype=np.float32)
        if self.transform is not None:
            img, target = self.transform(img, target)
        return {'img': img, 'target': target}


T = CustomCompose([ # FIXME: metti un nome piu pythoniano tipo train_transform
    CustomHorizontalFlip(p=0.5),
    CustomVerticalFlip(p=0.5),
    CustomToTensor(), # Normalmente si mette per ultimo il ToTensor. E' solo un fatto di stile, poi non cambia una minchia.
])

TD = CustomToTensor() # FIXME: metti un nome piu pythoniano tipo val_transform

def test():
    o_training_dts = VirusDataset(DTS_TRAIN_PATH, T)
    # print(len(o_training_dts))
    o_training_dtl = DataLoader(o_training_dts, shuffle=True, batch_size=32)
    # num_batch = 2
    # my_slice = list(o_training_dtl)[num_batch]['img'][1,1,:,:]
    # my_slice = my_slice * 255
    # cv2.imwrite('img.png', np.array(my_slice))

    for item in o_training_dtl:
        print(item['img'].shape)
        print(item['target'].shape)
        item['img'].to('cpu')

    for batch_idx, item in enumerate(o_training_dtl):
        print(f'i = {batch_idx}, item = {item["img"].shape}')
