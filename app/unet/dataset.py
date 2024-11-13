import os
from torch.utils.data import Dataset
from PIL import Image


class SegmentationDataset(Dataset):
    def __init__(self, image_dir, mask_dir, pairs_file=None, transform=None):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transform = transform

        self.image_files = sorted(
            [f for f in os.listdir(image_dir) if f.endswith((".jpg", ".png"))]
        )
        self.mask_files = sorted(
            [f for f in os.listdir(mask_dir) if f.endswith((".jpg", ".png"))]
        )

        assert len(self.image_files) == len(
            self.mask_files
        ), "이미지와 마스크 파일 수가 일치하지 않습니다."

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_path = os.path.join(self.image_dir, self.image_files[idx])
        mask_path = os.path.join(self.mask_dir, self.mask_files[idx])

        image = Image.open(image_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask
