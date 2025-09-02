# 地标识别系统

简洁的地标识别程序，支持桐梓林社区18个地标的识别。

## 📁 文件说明

- **`simple_landmark_recognition.py`** - 命令行版本，只输出地标名
- **`landmark_api.py`** - API服务版本，支持HTTP调用
- **`test_api.py`** - API测试脚本
- **`API使用说明.md`** - 详细的API使用文档

## 🚀 快速使用

### 命令行版本
```bash
python simple_landmark_recognition.py 图片路径
# 输出：成都宴 (桐梓林店)
```

### API版本
```bash
# 启动API服务
python landmark_api.py

# 使用curl测试
curl -X POST -F "image=@test.jpg" http://localhost:5000/recognize
```

## 📍 支持的地标

餐厅类：成都宴、柴门公馆、其心西餐厅、摩根扒房、四季锅火锅、卢记正街饭店、漾亚·雍雅合鲜、银滩鲍鱼火锅

酒吧类：氟西汀Whisky&Cocktail Bar、音乐房子

公共服务：社区活动中心、卫生中心

其他：桐梓林欧洲风情街、紫荆电影院、成都凯宾斯基饭店、成都首座万丽酒店、建设银行、宝利汇

## ⚙️ 环境要求

- Python 3.7+
- conda环境: `community_map_env`
- 依赖包: `torch torchvision Pillow flask`
- 模型文件: `image_detection/best_landmark_model_finetuned.pt` 