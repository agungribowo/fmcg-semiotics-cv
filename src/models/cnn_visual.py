"""
CNN Visual Model
================
Arsitektur CNN untuk ekstraksi fitur visual dari gambar produk FMCG.
Input: image (224, 224, 3)
Output: feature vector (512,)
"""

import torch
import torch.nn as nn


class VisualFeatureExtractor(nn.Module):
    def __init__(self, backbone: str = "resnet18", pretrained: bool = True):
        super().__init__()
        if backbone == "resnet18":
            from torchvision.models import resnet18
            weights = "DEFAULT" if pretrained else None
            self.backbone = resnet18(weights=weights)
            in_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
        else:
            raise ValueError(f"Unknown backbone: {backbone}")

        self.projector = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)
        return self.projector(features)


class CNNClassifier(nn.Module):
    """Visual-only classifier for semiotic classes."""

    def __init__(self, num_classes: int, backbone: str = "resnet18"):
        super().__init__()
        self.extractor = VisualFeatureExtractor(backbone)
        self.classifier = nn.Linear(512, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.extractor(x)
        return self.classifier(z)


if __name__ == "__main__":
    model = CNNClassifier(num_classes=10)
    dummy = torch.randn(4, 3, 224, 224)
    out = model(dummy)
    print(f"Output shape: {out.shape}")
