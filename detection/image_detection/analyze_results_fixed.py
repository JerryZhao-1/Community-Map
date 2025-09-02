#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import torch
import torch.nn as nn
from torchvision import datasets, models, transforms


def evaluate(model_path: str, data_dir: str = 'landmark_data'):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    data_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    dataset = datasets.ImageFolder(os.path.join(data_dir, 'val'), data_transforms)
    class_names = dataset.classes
    num_classes = len(class_names)

    loader = torch.utils.data.DataLoader(dataset, batch_size=8, shuffle=False, num_workers=0)

    model = models.mobilenet_v3_large(weights=None)
    num_ftrs = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(num_ftrs, num_classes)

    checkpoint = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint)
    model = model.to(device)
    model.eval()

    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    acc = 100.0 * correct / max(1, total)
    print(f"📊 验证集准确率: {acc:.2f}%  ({correct}/{total})")


if __name__ == '__main__':
    model_path = os.environ.get('EVAL_MODEL_PATH', 'best_landmark_model_finetuned.pt')
    data_dir = os.environ.get('LANDMARK_DATA_DIR', 'landmark_data')
    evaluate(model_path, data_dir)
