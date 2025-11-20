import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import os

DATASET_DIR = "dataset/splits"

BATCH = 16
EPOCHS = 10
LR = 1e-4

device = "mps" if torch.backends.mps.is_available() else "cpu"
print("Using device:", device)

# Image transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5]),
])

# Load datasets
train_ds = datasets.ImageFolder(os.path.join(DATASET_DIR, "train"), transform)
val_ds   = datasets.ImageFolder(os.path.join(DATASET_DIR, "val"),   transform)
test_ds  = datasets.ImageFolder(os.path.join(DATASET_DIR, "test"),  transform)

train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH)
test_loader  = DataLoader(test_ds,  batch_size=BATCH)

# Load pretrained model
model = models.resnet18(weights="DEFAULT")
model.fc = nn.Linear(model.fc.in_features, len(train_ds.classes))
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# Training Loop
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)

        optimizer.zero_grad()
        pred = model(imgs)
        loss = criterion(pred, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"[Epoch {epoch+1}/{EPOCHS}] Loss: {total_loss:.4f}")

print("Training complete!")

torch.save(model.state_dict(), "symbol_classifier.pth")
print("Saved model → symbol_classifier.pth")
