import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image

# 학습 시 클래스 순서와 동일하게 유지
CLASSES = ["excessive", "underrate", "norm"]

# ===== 모델 정의: 학습 스크립트와 동일 =====
class ConvEncoder(nn.Module):
    def __init__(self, latent_dim=256):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(inplace=True),

            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(inplace=True),

            nn.Conv2d(64, 128, 3, stride=2, padding=1),
            nn.BatchNorm2d(128), nn.ReLU(inplace=True),

            nn.Conv2d(128, 256, 3, stride=2, padding=1),
            nn.BatchNorm2d(256), nn.ReLU(inplace=True),

            nn.Conv2d(256, 512, 3, stride=2, padding=1),
            nn.BatchNorm2d(512), nn.ReLU(inplace=True),
        )
        self.flatten = nn.Flatten()
        # 입력 img_size=224 기준 -> 224→112→56→28→14→7
        self.fc_mu = nn.Linear(512 * 7 * 7, latent_dim)

    def forward(self, x):
        h = self.features(x)
        z = self.fc_mu(self.flatten(h))
        return z


class Classifier(nn.Module):
    def __init__(self, encoder: ConvEncoder, num_classes=3, latent_dim=256, dropout=0.2):
        super().__init__()
        self.encoder = encoder
        # 학습 스크립트와 동일한 head (Linear, ReLU, Dropout, Linear)
        self.head = nn.Sequential(
            nn.Linear(latent_dim, 256), nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        # 학습 때는 encoder를 freeze하고 head만 학습했지만
        # 추론에서는 grad 필요 없음
        z = self.encoder(x)
        return self.head(z)

# ===== 전처리: 학습 시 img_size=224와 동일하게 =====
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ===== 장치 선택 (GPU 우선) =====
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model(weight_path="classifier_best.pth"):
    encoder = ConvEncoder(latent_dim=256)
    model = Classifier(encoder, num_classes=len(CLASSES), latent_dim=256, dropout=0.2)
    # 체크포인트를 현재 장치로 로드
    state_dict = torch.load(weight_path, map_location=device)
    model.load_state_dict(state_dict)  # strict=True
    model.to(device)
    model.eval()
    return model

@torch.inference_mode()
def predict_image(img_path, model):
    img = Image.open(img_path).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)

    logits = model(x)
    pred_idx = int(torch.argmax(logits, dim=1).item())
    return CLASSES[pred_idx]
