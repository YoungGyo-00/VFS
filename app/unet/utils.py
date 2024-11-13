from PIL import Image
import numpy as np
import torch


# 추론 함수: 학습된 모델을 사용하여 마스크를 생성
def inference(model, image_path, transform, device):
    model.eval()
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image)
        mask = torch.sigmoid(output).cpu().squeeze(0).numpy() > 0.5

    return mask


# 결과를 이미지로 저장하는 함수
def save_result(mask, save_path):
    # 불필요한 차원을 제거
    mask = mask.squeeze()  # shape이 (128, 128)로 변경됨
    # 값을 0-255 범위로 조정하여 이미지로 변환
    result_image = Image.fromarray((mask * 255).astype(np.uint8))
    result_image.save(save_path)
