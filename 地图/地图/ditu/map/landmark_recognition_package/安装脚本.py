#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
地标识别模块自动化安装脚本
"""

import subprocess
import sys
import os

def install_dependencies():
    """安装依赖包"""
    print("🔧 安装Python依赖...")
    
    try:
        # 确保pip是最新版本
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 安装项目依赖
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", 
            "landmark_recognition/requirements.txt"
        ])
        print("✅ 依赖安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        print("💡 请尝试手动安装: pip install -r landmark_recognition/requirements.txt")
        return False

def verify_installation():
    """验证安装"""
    print("🔍 验证安装...")
    
    try:
        import torch
        import torchvision
        from PIL import Image
        import flask
        
        print(f"✅ PyTorch版本: {torch.__version__}")
        print(f"✅ TorchVision版本: {torchvision.__version__}")
        print(f"✅ PIL版本: {Image.__version__}")
        print(f"✅ Flask版本: {flask.__version__}")
        print(f"✅ CUDA可用: {torch.cuda.is_available()}")
        
        # 测试模型加载
        from landmark_recognition.django_landmark_service import get_landmark_service
        service = get_landmark_service()
        health = service.health_check()
        
        if health['is_loaded']:
            print("✅ 模型加载成功！")
            print(f"✅ 支持地标数量: {health['supported_landmarks_count']}")
            print("✅ 验证通过！")
            return True
        else:
            print("❌ 模型加载失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    print("🚀 开始安装地标识别模块...")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要Python 3.7+")
        return
    
    print(f"✅ Python版本: {sys.version}")
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 安装失败！")
        return
    
    print("\n" + "=" * 50)
    
    # 验证安装
    if not verify_installation():
        print("❌ 验证失败！")
        return
    
    print("\n" + "=" * 50)
    print("🎉 安装完成！")
    print("📖 请查看 '快速开始.md' 了解使用方法")
    print("🔧 开始Django集成请参考 'landmark_recognition/docs/部署说明.md'")

if __name__ == "__main__":
    main()
