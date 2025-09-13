# 地标识别包（Qwen 直连版）

仅发送本文件夹给他人即可使用。无需百度，默认只使用通义千问（DashScope）多模态；可选启用本地模型。

支持两种主要调用：
- 默认：`get_landmark` → 同时跑 Qwen 与本地模型，冲突以 Qwen 为准，返回 `{success, landmark}`
- 纯 Qwen：`get_landmark_qwen(..., return_details=True)` → 返回包含 raw 文本等调试信息

## 依赖安装
- 仅用 Qwen（最小集）：
```powershell
python -m pip install -r image_detection_package/requirements.txt
```
- Qwen + 本地模型（CPU，推荐一键）：
```powershell
python -m pip install -r image_detection_package/requirements_hybrid.txt
```
- 若需 GPU/CUDA，请按环境选择官方索引安装（示例 CUDA 12.1）：
```powershell
python -m pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision
```

## 配置环境变量
```powershell
$env:DASHSCOPE_API_KEY = "sk-xxxx"
```

## 默认：两个同时使用（以 Qwen 为准）
```python
from image_detection_package import get_landmark

res = get_landmark(r"D:\path\to\image.jpg")
print(res)  # {'success': True, 'landmark': '...'}
```

## 纯 Qwen（需要更多细节时）
```python
from image_detection_package import get_landmark_qwen

info = get_landmark_qwen(r"D:\path\to\image.jpg", return_details=True)
print(info)
```

## 目录批量（Qwen）
```python
from image_detection_package import get_landmarks_qwen_in_dir

results = get_landmarks_qwen_in_dir(r"D:\path\to\dir", return_details=True)
print(results)
```

## 说明
- Qwen 输出带 ```json 代码块时已自动处理。
- 候选地标优先；未命中则可返回识别到的其他店名（在 `get_landmark_qwen(..., return_details=True)` 的返回里可见）。
- 本地模型可选，需存在权重文件并安装 torch/torchvision。