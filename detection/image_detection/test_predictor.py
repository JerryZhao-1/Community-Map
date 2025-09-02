#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

CLASS_NAMES = [
    'Gilis', 'baolihui', 'ccb', 'chaimengongguan', 'chengduyan',
    'communitycenter', 'dianyingyuan', 'flouxetine', 'kaibinsiji', 'luji', 'morgan',
    'ouzhoufengqingjie', 'sijiguo', 'wanlijiudian', 'weishengzhongxin', 'yangya',
    'yingdangbaoyu', 'yinyuefangzi'
]

CHINESE = {
    'Gilis': '其心西餐厅','baolihui': '宝利汇','ccb': '建设银行','chaimengongguan': '柴门公馆 (桐梓林店)',
    'chengduyan': '成都宴 (桐梓林店)','communitycenter': '社区活动中心','dianyingyuan': '紫荆电影院',
    'flouxetine': '氟西汀Whisky&Cocktail Bar (桐梓林店)','kaibinsiji': '成都凯宾斯基饭店','luji': '卢记正街饭店·川湘菜',
    'morgan': '摩根扒房','ouzhoufengqingjie': '桐梓林欧洲风情街','sijiguo': '四季锅火锅 (桐梓林店)',
    'wanlijiudian': '成都首座万丽酒店','weishengzhongxin': '卫生中心','yangya': '漾亚·雍雅合鲜 (桐梓林店)',
    'yingdangbaoyu': '银滩鲍鱼火锅 (希望路店)','yinyuefangzi': '音乐房子 (玉林店)'
}

TRANSFORM = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def load_model(model_path: str, device):
    model = models.mobilenet_v3_large(weights=None)
    num_ftrs = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(num_ftrs, len(CLASS_NAMES))
    checkpoint = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint)
    model = model.to(device)
    model.eval()
    return model


def predict_image(model, image_path: str, device):
    img = Image.open(image_path).convert('RGB')
    x = TRANSFORM(img).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(x)
        prob = torch.softmax(outputs[0], dim=0)
        _, idx = torch.max(outputs, 1)
        en = CLASS_NAMES[idx.item()]
        zh = CHINESE.get(en, en)
        conf = prob[idx.item()].item() * 100
        return zh, conf


def main():
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model_path = os.environ.get('MODEL_PATH', 'best_landmark_model_finetuned.pt')
    test_img = os.environ.get('TEST_IMG', os.path.join('..','images','test1.jpg'))

    model = load_model(model_path, device)
    zh, conf = predict_image(model, test_img, device)
    print(f"预测: {zh} ({conf:.2f}%)")


if __name__ == '__main__':
    main()
