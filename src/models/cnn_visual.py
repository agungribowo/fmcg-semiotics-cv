"""
CNN Visual Model
================
Arsitektur CNN untuk ekstraksi fitur visual dari gambar produk FMCG.
Backbone: EfficientNetB0 (dipilih berdasarkan hasil eksperimen sebelumnya)
Input: image (224, 224, 3)
Output: feature vector (512,)
"""

import torch
import torch.nn as nn


class VisualFeatureExtractor(nn.Module):
    def __init__(self, backbone: str = "efficientnet_b0", pretrained: bool = True):
        super().__init__()
        if backbone == "efficientnet_b0":
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
            self.backbone = efficientnet_b0(weights=weights)
            in_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
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

    def __init__(self, num_classes: int, backbone: str = "efficientnet_b0"):
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
