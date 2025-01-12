print("""

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision import datasets
from tqdm import tqdm

# Check for GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Step 1: Define the CNN model using PyTorch
class CNNModel(nn.Module):
    def __init__(self):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128 * 4 * 4, 512)  # Adjust according to image size after pooling
        self.fc2 = nn.Linear(512, 10)  # For CIFAR-10, 10 classes
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))
        x = x.view(-1, 128 * 4 * 4)  # Flatten the tensor
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# Step 2: Define transformations for CIFAR-10 and CIFAR-100
train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(32, padding=4),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# Step 3: Load and preprocess CIFAR-10 dataset
print("\nLoading CIFAR-10 dataset...")
trainset = datasets.CIFAR10(root='./data', train=True, download=True, transform=train_transform)
testset = datasets.CIFAR10(root='./data', train=False, download=True, transform=test_transform)
trainloader = DataLoader(trainset, batch_size=64, shuffle=True)
testloader = DataLoader(testset, batch_size=64, shuffle=False)
print("CIFAR-10 dataset loaded successfully.")

# Step 4: Instantiate the model, define the loss function, and set up the optimizer
model = CNNModel().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=2, factor=0.5)

# Step 5: Model Checkpointing
best_acc = 0.0
checkpoint_path = './cnn_cifar10_best.pth'

# Step 6: Train the model
print("\nStarting training on CIFAR-10...")
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in tqdm(trainloader, desc=f'Epoch {epoch+1}/{num_epochs}'):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    scheduler.step(running_loss)
    train_acc = 100 * correct / total
    avg_loss = running_loss / len(trainloader)

    print(f"Epoch {epoch+1} Summary: Loss = {avg_loss:.4f}, Training Accuracy = {train_acc:.2f}%")

    if train_acc > best_acc:
        best_acc = train_acc
        torch.save(model.state_dict(), checkpoint_path)
        print(f"New best model saved with accuracy: {best_acc:.2f}%")

# Step 7: Evaluate the model on the CIFAR-10 test set
print("\nEvaluating the model on CIFAR-10 test set...")
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for inputs, labels in tqdm(testloader, desc='Testing'):
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

test_acc = 100 * correct / total
print(f"CIFAR-10 Test Accuracy: {test_acc:.2f}%")

# Step 8: Retrain the model with CIFAR-100
print("\nLoading CIFAR-100 dataset and retraining the model...")
trainset_100 = datasets.CIFAR100(root='./data', train=True, download=True, transform=train_transform)
testset_100 = datasets.CIFAR100(root='./data', train=False, download=True, transform=test_transform)
trainloader_100 = DataLoader(trainset_100, batch_size=64, shuffle=True)
testloader_100 = DataLoader(testset_100, batch_size=64, shuffle=False)

model.fc2 = nn.Linear(512, 100).to(device)
num_epochs = 5

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in tqdm(trainloader_100, desc=f'Retraining Epoch {epoch+1}/{num_epochs}'):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    scheduler.step(running_loss)
    train_acc = 100 * correct / total
    avg_loss = running_loss / len(trainloader_100)
    print(f"Epoch {epoch+1} Summary: Loss = {avg_loss:.4f}, Training Accuracy = {train_acc:.2f}%")

# Step 9: Evaluate the model on the CIFAR-100 test set
print("\nEvaluating the model on CIFAR-100 test set...")
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for inputs, labels in tqdm(testloader_100, desc='Testing'):
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

test_acc = 100 * correct / total
print(f"CIFAR-100 Test Accuracy: {test_acc:.2f}%")
""")