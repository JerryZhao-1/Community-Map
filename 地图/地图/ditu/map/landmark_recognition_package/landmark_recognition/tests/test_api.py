#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import base64
import json

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    response = requests.get('http://localhost:5000/health')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_landmarks_list():
    """测试获取地标列表接口"""
    print("📋 测试获取地标列表接口...")
    response = requests.get('http://localhost:5000/landmarks')
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"支持的地标数量: {data['total_count']}")
    print(f"前5个地标: {data['supported_landmarks'][:5]}")
    print()

def test_file_upload():
    """测试文件上传识别"""
    print("🖼️ 测试文件上传识别...")
    
    # 测试多张图片
    test_images = ['images/test1.jpg', 'images/test2.jpg', 'images/test3.jpeg']
    
    for image_path in test_images:
        try:
            with open(image_path, 'rb') as f:
                response = requests.post(
                    'http://localhost:5000/recognize',
                    files={'image': f}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {image_path}: {data['landmark']} (置信度: {data.get('confidence', 'N/A')}%)")
                else:
                    print(f"❌ {image_path}: 失败 - {response.text}")
                    
        except FileNotFoundError:
            print(f"⚠️ {image_path}: 文件不存在")
        except Exception as e:
            print(f"❌ {image_path}: 错误 - {e}")
    print()

def test_base64_recognition():
    """测试Base64识别"""
    print("🔤 测试Base64识别...")
    
    try:
        # 读取图片并转换为base64
        with open('images/test1.jpg', 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode()
        
        response = requests.post(
            'http://localhost:5000/recognize',
            json={'image_base64': image_base64}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Base64识别成功: {data['landmark']} (置信度: {data.get('confidence', 'N/A')}%)")
        else:
            print(f"❌ Base64识别失败: {response.text}")
            
    except Exception as e:
        print(f"❌ Base64识别错误: {e}")
    print()

def main():
    """运行所有测试"""
    print("🚀 开始API功能测试")
    print("=" * 50)
    
    try:
        test_health()
        test_landmarks_list()
        test_file_upload()
        test_base64_recognition()
        
        print("✅ 所有测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保服务已启动")
        print("   启动命令: python landmark_api.py")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

if __name__ == "__main__":
    main() 