import torch
from model import SimpleCNN
from trainer import Trainer
from data_utils import get_data_loaders

def main():
    # Load data
    train_loader, val_loader = get_data_loaders()
    
    # Initialize model
    model = SimpleCNN()
    
    # Check for CUDA
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    # Train and evaluate
    trainer = Trainer(model)
    trainer.train(train_loader, epochs=5, lr=0.001)
    trainer.evaluate(val_loader)

if __name__ == "__main__":
    main()
