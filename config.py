#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 模型配置
MODEL_CONFIG = {
    'model_path': BASE_DIR / 'image_detection' / 'best_landmark_model_finetuned.pt',
    'backup_model_path': BASE_DIR / 'image_detection' / 'best_landmark_model_fixed_extractor.pt',
    'device': 'auto',  # 'auto', 'cuda', 'cpu'
    'num_classes': 18,
    'image_size': 224,
    'batch_size': 1,
}

# API配置
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'max_content_length': 16 * 1024 * 1024,  # 16MB最大上传文件大小
}

# 图像处理配置
IMAGE_CONFIG = {
    'allowed_extensions': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'},
    'max_image_size': (2048, 2048),  # 最大图像尺寸
    'convert_to_rgb': True,
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': BASE_DIR / 'logs' / 'landmark_recognition.log',
}

# Django集成配置
DJANGO_CONFIG = {
    'media_root': '/tmp/uploads',  # Django媒体文件根目录
    'static_root': '/tmp/static',  # Django静态文件根目录
    'allowed_hosts': ['*'],  # 允许的主机
}

# 性能配置
PERFORMANCE_CONFIG = {
    'enable_cache': True,
    'cache_size': 100,  # 缓存预测结果数量
    'max_concurrent_requests': 10,  # 最大并发请求数
}

# 环境变量支持
def get_env_value(key, default=None):
    """从环境变量获取配置值"""
    return os.environ.get(key, default)

# 动态配置更新
if get_env_value('DJANGO_SETTINGS_MODULE'):
    # Django环境下的配置调整
    try:
        from django.conf import settings
        if hasattr(settings, 'MEDIA_ROOT'):
            DJANGO_CONFIG['media_root'] = settings.MEDIA_ROOT
        if hasattr(settings, 'STATIC_ROOT'):
            DJANGO_CONFIG['static_root'] = settings.STATIC_ROOT
    except ImportError:
        pass

# 生产环境配置
if get_env_value('PRODUCTION', 'false').lower() == 'true':
    API_CONFIG['debug'] = False
    LOGGING_CONFIG['level'] = 'WARNING'
    PERFORMANCE_CONFIG['enable_cache'] = True
