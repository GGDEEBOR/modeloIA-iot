from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
import timm
from torchvision import transforms


@dataclass(frozen=True)
class ImageModelConfig:
    weights_path: str
    device: str = "cpu"


class FireImageClassifier:
    """
    Modelo binario FIRE vs NO_FIRE.
    Output: probabilidad de FIRE (0..1)
    """
    def __init__(self, cfg: ImageModelConfig) -> None:
        self.device = torch.device(cfg.device)

        # Arquitectura consistente con train_image.py
        self.model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=1)
        self.model.eval()
        self.model.to(self.device)

        wpath = Path(cfg.weights_path)
        if not wpath.exists():
            raise FileNotFoundError(
                f"No se encontraron pesos de modelo en {wpath}. "
                "Entrena con scripts/train_image.py o coloca el .pt."
            )

        state = torch.load(str(wpath), map_location="cpu")
        self.model.load_state_dict(state)

        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225),
            ),
        ])

        self.sigmoid = nn.Sigmoid()

    @torch.no_grad()
    def predict_proba(self, img_path: str) -> float:
        img = Image.open(img_path).convert("RGB")
        x = self.preprocess(img).unsqueeze(0).to(self.device)  # [1,3,224,224]
        logits = self.model(x)  # [1,1]
        prob = self.sigmoid(logits).item()
        return float(prob)
