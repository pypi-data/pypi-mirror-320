import torch
from unikan import UniversalKAN
import unikan.basis as basis
import torchvision
from torch.utils.data import DataLoader

# Select device, prioritize GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Build SKAN network with 784 input nodes, 100 hidden nodes, and 10 output nodes
# net = UniversalKAN([784, 100, 10], device=device) # default

function_lists = [
    [
        {'function': basis.lshifted_softplus, 'param_num': 1, 'node_type': 'add', 'node_num': 90, 'use_bias': True},
        {'function': basis.lshifted_softplus, 'param_num': 1, 'node_type': 'mul', 'node_num': 10, 'use_bias': True}
        ],
    [
        {'function': basis.lshifted_softplus, 'param_num': 1, 'node_type': 'add', 'node_num': 10, 'use_bias': True}
        ] 
    ]
net = UniversalKAN([784, 100, 10], function_lists=function_lists, device=device)

# Use MNIST dataset
transform = torchvision.transforms.Compose([
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Lambda(lambda x: x.view(-1))
])
train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

lr = 0.0004

# Select Adam optimizer
optimizer = torch.optim.Adam(net.parameters(), lr=lr)
# Select Cross Entropy Loss function
criterion = torch.nn.CrossEntropyLoss()

# Train the network
for epoch in range(10):
    net.train()
    for i, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = net(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if i % 100 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, i * len(data), len(train_loader.dataset),
                100. * i / len(train_loader), loss.item()))