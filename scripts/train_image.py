from __future__ import annotations

import os
from pathlib import Path
import random

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import ImageFolder
from torchvision import transforms
import timm

def main():
    data_dir = Path("data")
    out_path = Path("models/image_fire.pt")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tfm_train = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize((0.485,0.456,0.406), (0.229,0.224,0.225)),
    ])
    tfm_val = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize((0.485,0.456,0.406), (0.229,0.224,0.225)),
    ])

    ds = ImageFolder(root=str(data_dir), transform=tfm_train)
    n = len(ds)
    if n < 50:
        print(f"[WARN] Dataset pequeño ({n}). Igual se puede fine-tunear, pero cuidado con overfitting.")

    val_size = max(1, int(0.2 * n))
    train_size = n - val_size
    ds_train, ds_val = random_split(ds, [train_size, val_size])

    # Cambiar transform del val
    ds_val.dataset.transform = tfm_val

    dl_train = DataLoader(ds_train, batch_size=16, shuffle=True, num_workers=0)
    dl_val   = DataLoader(ds_val, batch_size=16, shuffle=False, num_workers=0)


    # Modelo binario: 1 logit
    model = timm.create_model("efficientnet_b0", pretrained=True, num_classes=1)
    model.to(device)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)

    best_val = 0.0
    for epoch in range(1, 6):  # 5 épocas: suficiente para IoT demo
        model.train()
        total_loss = 0.0

        for x, y in dl_train:
            x = x.to(device)
            y = y.float().to(device).unsqueeze(1)  # [B,1]  (fire=1, no_fire=0)
            logits = model(x)
            loss = criterion(logits, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        # Validación simple por accuracy con threshold 0.5
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in dl_val:
                x = x.to(device)
                y = y.to(device)
                logits = model(x).squeeze(1)
                probs = torch.sigmoid(logits)
                preds = (probs >= 0.5).long()
                correct += (preds.cpu() == y).sum().item()
                total += y.size(0)

        val_acc = correct / max(1, total)
        avg_loss = total_loss / max(1, len(dl_train))
        print(f"Epoch {epoch} | train_loss={avg_loss:.4f} | val_acc={val_acc:.3f}")

        if val_acc >= best_val:
            best_val = val_acc
            torch.save(model.state_dict(), str(out_path))
            print(f"  -> Guardado mejor modelo en {out_path} (val_acc={best_val:.3f})")

    print("Entrenamiento terminado.")

if __name__ == "__main__":
    main()
