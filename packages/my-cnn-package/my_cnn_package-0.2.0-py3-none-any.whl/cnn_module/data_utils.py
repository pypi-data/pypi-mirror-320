import torch
from torchvision import datasets, transforms

def get_data_loaders(data_dir=None, batch_size=64):
    transform = transforms.Compose([
        transforms.Resize((28, 28)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    
    if data_dir:
        train_dataset = datasets.ImageFolder(data_dir + '/train', transform=transform)
        val_dataset = datasets.ImageFolder(data_dir + '/val', transform=transform)
    else:
        train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
        val_dataset = datasets.MNIST(root='./data', train=False, transform=transform, download=True)
    
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader
