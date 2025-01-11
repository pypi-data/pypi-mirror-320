# Gói CNN Module


## Tổng quan

`my_cnn_package` là một gói Python nhẹ và linh hoạt được xây dựng trên nền tảng PyTorch, giúp bạn dễ dàng tạo, huấn luyện và đánh giá các mô hình Mạng Nơ-ron Tích chập (CNN). Gói này được thiết kế để đơn giản hóa quy trình làm việc với CNN, hỗ trợ cả dữ liệu chuẩn (như MNIST) và dữ liệu tùy chỉnh của người dùng. Nó rất phù hợp cho người mới học, các nhà nghiên cứu, hoặc nhà phát triển muốn nhanh chóng tạo nguyên mẫu và triển khai mô hình học sâu vào thực tế.

### Tính năng nổi bật

- **Mô hình CNN linh hoạt**: Bạn có thể dễ dàng tùy chỉnh kiến trúc của CNN theo nhu cầu.
- **Hỗ trợ dữ liệu tích hợp**: Bao gồm các tiện ích để làm việc với các tập dữ liệu phổ biến như MNIST hoặc dữ liệu do người dùng cung cấp.
- **Tiện ích huấn luyện**: Vòng lặp huấn luyện được tối ưu hóa, hỗ trợ GPU nếu có.
- **Ví dụ trực quan**: Một ví dụ hoàn chỉnh được tích hợp để giúp người dùng hiểu nhanh quy trình.
- **Mở rộng dễ dàng**: Thiết kế để dễ dàng tích hợp vào các dự án học sâu khác sử dụng PyTorch.

---

## Cài đặt

Gói này đã được đăng tải trên PyPI, bạn có thể cài đặt nhanh chóng bằng lệnh:

```bash
pip install my-cnn-package
-- 
```
## Chạy code:
```python
import torch
from model import SimpleCNN
from trainer import Trainer
from data_utils import get_data_loaders

def main():
    # Load data
    train_loader, val_loader = get_data_loaders(your data dir)
    
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
