# Landmark Recognition Package

This package provides a hybrid landmark recognition service using a local PyTorch model and the Baidu Facade Recognition API.

## Installation

```bash
pip install -e .
```

## Usage

```python
from image_detection_package.recognition_dispatcher import recognize_image_hybrid
from image_detection_package.baidu_facade_service import BaiduFacadeService

# Initialize the Baidu service with your credentials (optional)
baidu_service = BaiduFacadeService(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")

with open("path/to/your/image.jpg", "rb") as f:
    results = recognize_image_hybrid(f, baidu_service_instance=baidu_service)

print(results)
```
