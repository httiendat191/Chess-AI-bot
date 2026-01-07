import torch
import torch.nn as nn

class ChessNet(nn.Module):
    def __init__(self):
        super(ChessNet, self).__init__()
        # Input: 12 channels (6 trắng + 6 đen) x 8 x 8
        
        # Block 1: Trích xuất đặc trưng cơ bản
        self.conv1 = nn.Conv2d(12, 32, kernel_size=3, padding=1)
        self.bn1   = nn.BatchNorm2d(32)
        self.relu1 = nn.ReLU()
        
        # Block 2: Trích xuất đặc trưng phức tạp hơn
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2   = nn.BatchNorm2d(64)
        self.relu2 = nn.ReLU()

        # Block 3: Tăng chiều sâu 
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3   = nn.BatchNorm2d(128)
        self.relu3 = nn.ReLU()
        
        # Flatten
        self.flatten = nn.Flatten()
        
        # Fully Connected Layers với Dropout
        # Input size: 128 channels * 8 * 8 = 8192
        self.fc1 = nn.Linear(128 * 8 * 8, 512)
        self.dropout1 = nn.Dropout(0.3) # Giúp tránh học vẹt
        self.relu4 = nn.ReLU()
        
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.3)
        self.relu5 = nn.ReLU()
        
        self.fc3 = nn.Linear(256, 1) # Output: 1 giá trị score (-1 đến 1)

    def forward(self, x):
        x = self.relu1(self.bn1(self.conv1(x)))
        x = self.relu2(self.bn2(self.conv2(x)))
        x = self.relu3(self.bn3(self.conv3(x)))
        
        x = self.flatten(x)
        x = self.relu4(self.dropout1(self.fc1(x)))
        x = self.relu5(self.dropout2(self.fc2(x)))
        x = self.fc3(x)
        return x