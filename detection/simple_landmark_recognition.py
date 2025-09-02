#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的地标识别命令行工具
支持桐梓林社区18个地标的识别
使用方法: python simple_landmark_recognition.py 图片路径
输出: 地标名称
"""

import sys
import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import argparse

class SimpleLandmarkRecognizer:
    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        # 数据预处理
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        # 地标名称
        self.class_names = [
            'Gilis', 'baolihui', 'ccb', 'chaimengongguan', 'chengduyan', 
            'communitycenter', 'dianyingyuan', 'flouxetine', 'kaibinsiji', 'luji', 'morgan', 
            'ouzhoufengqingjie', 'sijiguo', 'wanlijiudian', 'weishengzhongxin', 'yangya', 
            'yingdangbaoyu', 'yinyuefangzi'
        ]
        
        # 中文名称映射
        self.chinese_names = {
            'Gilis': '其心西餐厅',
            'baolihui': '宝利汇',
            'ccb': '建设银行',
            'chaimengongguan': '柴门公馆 (桐梓林店)',
            'chengduyan': '成都宴 (桐梓林店)',
            'communitycenter': '社区活动中心',
            'dianyingyuan': '紫荆电影院',
            'flouxetine': '氟西汀Whisky&Cocktail Bar (桐梓林店)',
            'kaibinsiji': '成都凯宾斯基饭店',
            'luji': '卢记正街饭店·川湘菜',
            'morgan': '摩根扒房',
            'ouzhoufengqingjie': '桐梓林欧洲风情街',
            'sijiguo': '四季锅火锅 (桐梓林店)',
            'wanlijiudian': '成都首座万丽酒店',
            'weishengzhongxin': '卫生中心',
            'yangya': '漾亚·雍雅合鲜 (桐梓林店)',
            'yingdangbaoyu': '银滩鲍鱼火锅 (希望路店)',
            'yinyuefangzi': '音乐房子 (玉林店)'
        }
        
        # 加载模型
        self._load_model()
    
    def _load_model(self):
        """加载训练好的模型"""
        try:
            # 获取模型文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'image_detection', 'best_landmark_model_finetuned.pt')
            
            # 检查模型文件是否存在
            if not os.path.exists(model_path):
                print(f"❌ 错误: 模型文件不存在: {model_path}")
                sys.exit(1)
            
            # 创建模型
            self.model = models.mobilenet_v3_large(weights=None)
            num_ftrs = self.model.classifier[3].in_features
            self.model.classifier[3] = nn.Linear(num_ftrs, len(self.class_names))
            
            # 加载权重
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
            self.model.load_state_dict(checkpoint)
            self.model = self.model.to(self.device)
            self.model.eval()
            
        except Exception as e:
            print(f"❌ 错误: 加载模型失败: {str(e)}")
            sys.exit(1)
    
    def recognize(self, image_path):
        """识别图片中的地标"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"❌ 错误: 图片文件不存在: {image_path}")
                return None
            
            # 加载图片
            image = Image.open(image_path).convert('RGB')
            
            # 预处理
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # 预测
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                _, predicted = torch.max(outputs, 1)
                predicted_english = self.class_names[predicted.item()]
                landmark_name = self.chinese_names.get(predicted_english, "无法识别")
                confidence = probabilities[predicted.item()].item() * 100
                
                return landmark_name
                
        except Exception as e:
            print(f"❌ 错误: 识别失败: {str(e)}")
            return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='简单的地标识别工具')
    parser.add_argument('image_path', help='图片文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    # 创建识别器
    recognizer = SimpleLandmarkRecognizer()
    
    # 执行识别
    result = recognizer.recognize(args.image_path)
    
    if result:
        if args.verbose:
            print(f"📸 图片: {args.image_path}")
            print(f"📍 识别结果: {result}")
        else:
            print(result)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
