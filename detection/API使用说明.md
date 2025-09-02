# 地标识别API使用说明

## 快速开始

### 1. 安装依赖
```bash
pip install flask torch torchvision Pillow
```

### 2. 启动API服务
```bash
python landmark_api.py
```

服务将在 `http://localhost:5000` 启动

## API接口

### 1. 健康检查
```
GET /health
```

**响应示例：**
```json
{
  "status": "ok",
  "message": "地标识别API运行正常"
}
```

### 2. 地标识别
```
POST /recognize
```

**支持两种方式：**

#### 方式1：文件上传
```bash
curl -X POST -F "image=@test.jpg" http://localhost:5000/recognize
```

#### 方式2：Base64编码
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="}' \
  http://localhost:5000/recognize
```

**响应示例：**
```json
{
  "success": true,
  "landmark": "成都宴 (桐梓林店)",
  "confidence": 99.09
}
```

### 3. 获取支持的地标列表
```
GET /landmarks
```

**响应示例：**
```json
{
  "supported_landmarks": [
    "其心西餐厅",
    "宝利汇",
    "建设银行",
    "柴门公馆 (桐梓林店)",
    "成都宴 (桐梓林店)",
    "社区活动中心",
    "紫荆电影院",
    "氟西汀Whisky&Cocktail Bar (桐梓林店)",
    "成都凯宾斯基饭店",
    "卢记正街饭店·川湘菜",
    "摩根扒房",
    "桐梓林欧洲风情街",
    "四季锅火锅 (桐梓林店)",
    "成都首座万丽酒店",
    "卫生中心",
    "漾亚·雍雅合鲜 (桐梓林店)",
    "银滩鲍鱼火锅 (希望路店)",
    "音乐房子 (玉林店)"
  ],
  "total_count": 18
}
```

## 使用示例

### Python调用示例
```python
import requests

# 文件上传方式
with open('test.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/recognize',
        files={'image': f}
    )
    result = response.json()
    print(f"地标: {result['landmark']}")
    print(f"置信度: {result['confidence']}%")

# Base64方式
import base64
with open('test.jpg', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    'http://localhost:5000/recognize',
    json={'image_base64': image_base64}
)
result = response.json()
print(f"地标: {result['landmark']}")
```

### JavaScript调用示例
```javascript
// 文件上传方式
const formData = new FormData();
formData.append('image', file);

fetch('http://localhost:5000/recognize', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('地标:', data.landmark);
    console.log('置信度:', data.confidence + '%');
});

// Base64方式
fetch('http://localhost:5000/recognize', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        image_base64: base64String
    })
})
.then(response => response.json())
.then(data => {
    console.log('地标:', data.landmark);
});
```

## 错误处理

### 常见错误响应

**文件格式错误：**
```json
{
  "error": "识别失败: cannot identify image file"
}
```

**未提供图片：**
```json
{
  "error": "请提供图片文件或base64编码的图片数据"
}
```

**服务器错误：**
```json
{
  "error": "识别失败: 模型加载失败"
}
```

## 部署说明

### 生产环境部署
```bash
# 使用gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 landmark_api:app
```

### Docker部署
创建 `Dockerfile`：
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install flask torch torchvision Pillow

EXPOSE 5000

CMD ["python", "landmark_api.py"]
```

构建和运行：
```bash
docker build -t landmark-api .
docker run -p 5000:5000 landmark-api
``` 