# 桐梓林社区地标识别预测器使用指南（简版）

## 模型信息
- 架构: MobileNetV3-Large
- 权重: `best_landmark_model_finetuned.pt`
- 类别数: 18

## 单张图片预测
```bash
python test_predictor.py
# 或指定模型与图片
MODEL_PATH=best_landmark_model_finetuned.pt TEST_IMG=../images/test1.jpg python test_predictor.py
```

## 训练
```bash
# 需准备数据集: landmark_data/train 与 landmark_data/val
python train_mobilenetv3_landmarks.py
```

## 评估
```bash
EVAL_MODEL_PATH=best_landmark_model_finetuned.pt LANDMARK_DATA_DIR=landmark_data \
python analyze_results_fixed.py
```

## 工具
- `rename_images.py`: 重命名数据集图片为 image001.jpg 等
- `split_dataset.py`: 按比例从 train 划分一部分到 val
