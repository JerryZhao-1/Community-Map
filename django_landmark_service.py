#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import base64
import logging
from django.conf import settings

class DjangoLandmarkService:
    """
    为Django后端专门设计的地标识别服务
    """
    
    def __init__(self, model_path=None):
        """
        初始化地标识别服务
        
        Args:
            model_path: 模型文件路径，如果为None则使用默认路径
        """
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        # 设置模型路径
        if model_path is None:
            self.model_path = os.path.join(
                os.path.dirname(__file__), 
                'image_detection', 
                'best_landmark_model_finetuned.pt'
            )
        else:
            self.model_path = model_path
        
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
        
        # 初始化模型
        self.model = None
        self.is_loaded = False
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 加载模型
        self.load_model()
    
    def load_model(self):
        """加载模型"""
        try:
            self.logger.info(f"正在加载模型: {self.model_path}")
            
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"模型文件不存在: {self.model_path}")
            
            # 创建模型架构
            self.model = models.mobilenet_v3_large(weights=None)
            num_ftrs = self.model.classifier[3].in_features
            self.model.classifier[3] = nn.Linear(num_ftrs, len(self.class_names))
            
            # 加载训练好的权重
            checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=True)
            self.model.load_state_dict(checkpoint)
            
            # 设置为评估模式
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            self.logger.info("模型加载成功")
            
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            self.is_loaded = False
            raise
    
    def recognize_from_django_file(self, django_file):
        """
        从Django UploadedFile对象识别地标
        
        Args:
            django_file: Django的InMemoryUploadedFile或TemporaryUploadedFile对象
            
        Returns:
            dict: 识别结果
        """
        try:
            if not self.is_loaded:
                raise RuntimeError("模型未加载")
            
            # 处理Django文件对象
            if hasattr(django_file, 'read'):
                image_data = django_file.read()
                image = Image.open(io.BytesIO(image_data)).convert('RGB')
            else:
                # 如果是文件路径
                image = Image.open(django_file).convert('RGB')
            
            return self._predict(image)
            
        except Exception as e:
            self.logger.error(f"识别失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'landmark': None,
                'confidence': 0
            }
    
    def recognize_from_base64(self, base64_string):
        """
        从base64字符串识别地标
        
        Args:
            base64_string: base64编码的图片字符串
            
        Returns:
            dict: 识别结果
        """
        try:
            if not self.is_loaded:
                raise RuntimeError("模型未加载")
            
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            return self._predict(image)
            
        except Exception as e:
            self.logger.error(f"Base64识别失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'landmark': None,
                'confidence': 0
            }
    
    def recognize_from_path(self, image_path):
        """
        从文件路径识别地标
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            dict: 识别结果
        """
        try:
            if not self.is_loaded:
                raise RuntimeError("模型未加载")
            
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            image = Image.open(image_path).convert('RGB')
            return self._predict(image)
            
        except Exception as e:
            self.logger.error(f"路径识别失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'landmark': None,
                'confidence': 0
            }
    
    def _predict(self, image):
        """
        执行预测
        
        Args:
            image: PIL Image对象
            
        Returns:
            dict: 预测结果
        """
        try:
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                _, predicted = torch.max(outputs, 1)
                
                predicted_english = self.class_names[predicted.item()]
                landmark_name = self.chinese_names.get(predicted_english, "无法识别")
                confidence = probabilities[predicted.item()].item() * 100
                
                return {
                    'success': True,
                    'landmark': landmark_name,
                    'landmark_english': predicted_english,
                    'confidence': round(confidence, 2),
                    'error': None
                }
                
        except Exception as e:
            self.logger.error(f"预测失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'landmark': None,
                'confidence': 0
            }
    
    def get_supported_landmarks(self):
        """获取支持的地标列表"""
        return {
            'landmarks': list(self.chinese_names.values()),
            'total_count': len(self.chinese_names)
        }
    
    def health_check(self):
        """健康检查"""
        return {
            'is_loaded': self.is_loaded,
            'device': str(self.device),
            'model_path': self.model_path,
            'supported_landmarks_count': len(self.class_names)
        }

# 创建全局实例（可选）
landmark_service = None

def get_landmark_service():
    """获取地标识别服务实例（单例模式）"""
    global landmark_service
    if landmark_service is None:
        landmark_service = DjangoLandmarkService()
    return landmark_service
