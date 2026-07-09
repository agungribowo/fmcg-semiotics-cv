"""
Multimodal Fusion Model
=======================
Menggabungkan fitur visual (CNN) dan fitur teks (OCR) untuk klasifikasi
semiotik produk FMCG.
"""

import torch
import torch.nn as nn

from src.models.cnn_visual import VisualFeatureExtractor


class TextFeatureExtractor(nn.Module):
    """Simple text encoder for OCR token sequences."""

    def __init__(self, vocab_size: int = 1000, embed_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(x)
        _, (h_n, _) = self.lstm(emb)
        return torch.cat((h_n[0], h_n[1]), dim=1)


class MultimodalFusion(nn.Module):
    def __init__(
        self,
        num_classes: int,
        vocab_size: int = 1000,
        fusion_dim: int = 512,
    ):
        super().__init__()
        self.visual_encoder = VisualFeatureExtractor()
        self.text_encoder = TextFeatureExtractor(vocab_size=vocab_size)

        fusion_input_dim = 512 + 512  # visual(512) + text(512 bidirectional)
        self.fusion = nn.Sequential(
            nn.Linear(fusion_input_dim, fusion_dim),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(fusion_dim, num_classes),
        )

    def forward(self, image: torch.Tensor, text: torch.Tensor) -> torch.Tensor:
        v_feat = self.visual_encoder(image)
        t_feat = self.text_encoder(text)
        combined = torch.cat([v_feat, t_feat], dim=1)
        return self.fusion(combined)


if __name__ == "__main__":
    model = MultimodalFusion(num_classes=10)
    dummy_img = torch.randn(4, 3, 224, 224)
    dummy_txt = torch.randint(0, 100, (4, 20))
    out = model(dummy_img, dummy_txt)
    print(f"Output shape: {out.shape}")
