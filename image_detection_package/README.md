# Landmark Recognition Package

This package provides a hybrid landmark recognition service using a local PyTorch model and the Baidu Facade Recognition API.

## Installation

```bash
pip install -e .
```

## Usage

The package is designed to be very simple to use. The main function is `get_landmark`.

```python
from image_detection_package import get_landmark

# --- Example 1: Using only the local model ---
landmark_name = get_landmark("path/to/your/image.jpg")
if landmark_name:
    print(f"The landmark is: {landmark_name}")
else:
    print("Landmark not recognized.")

# --- Example 2: Using the hybrid model (local + Baidu) ---
landmark_name_hybrid = get_landmark(
    "path/to/your/image.jpg",
    baidu_api_key="YOUR_BAIDU_API_KEY",
    baidu_secret_key="YOUR_BAIDU_SECRET_KEY"
)
if landmark_name_hybrid:
    print(f"The landmark (hybrid result) is: {landmark_name_hybrid}")
else:
    print("Landmark not recognized by either service.")
```