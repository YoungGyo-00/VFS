import os
import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from dataset import SegmentationDataset
from model import UNet
from utils import inference, save_result

# 하이퍼파라미터 및 경로 설정
EPOCHS = 40
BATCH_SIZE = 4
LEARNING_RATE = 0.001
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
# DEVICE = "cpu"
print(f"Using device: {DEVICE}")
OUTPUT_DIR = "./output/models"
RESULTS_DIR = "./output/results"

# 데이터 변환 설정
transform = transforms.Compose([transforms.Resize((256, 256)), transforms.ToTensor()])

# 데이터셋 로드
train_dataset = SegmentationDataset(
    "./dataset/train/image",
    "./dataset/train/image-mask",
    None,
    transform=transform,
)

subset_indices = list(range(len(train_dataset) // 10))  # 데이터의 10%만 사용
train_subset = Subset(train_dataset, subset_indices)
train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True)

# 모델, 손실 함수, 옵티마이저 설정
model = UNet(in_channels=3, out_channels=1).to(DEVICE)
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)


# 학습 함수
def train(model, loader, criterion, optimizer):
    model.train()
    for epoch in range(EPOCHS):
        epoch_loss = 0.0
        print(f"Epoch [{epoch+1}/{EPOCHS}] 시작")

        for batch_idx, (images, masks) in enumerate(loader):
            images, masks = images.to(DEVICE), masks.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, masks)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            batch_loss = loss.item()
            epoch_loss += batch_loss

            # 각 배치마다 손실 출력
            if batch_idx % 10 == 0:  # 10번째 배치마다 로그 출력
                print(
                    f"Batch [{batch_idx}/{len(loader)}], Batch Loss: {batch_loss:.4f}"
                )

        # 에포크가 끝날 때 에포크 손실 출력
        print(f"Epoch [{epoch+1}/{EPOCHS}], Epoch Loss: {epoch_loss/len(loader):.4f}")

        # 모델 저장
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        torch.save(
            model.state_dict(), os.path.join(OUTPUT_DIR, f"unet_epoch_{epoch+1}.pth")
        )


# 학습 실행
if __name__ == "__main__":
    train(model, train_loader, criterion, optimizer)

    # 테스트 이미지에 대한 추론 예시
    test_image_path = "./dataset/test/image/000001_0.jpg"
    mask = inference(model, test_image_path, transform, DEVICE)

    # 추론 결과 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    save_result(mask, os.path.join(RESULTS_DIR, "result_image.png"))
