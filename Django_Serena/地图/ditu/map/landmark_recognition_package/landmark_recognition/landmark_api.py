#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import base64

app = Flask(__name__)

class LandmarkAPI:
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
        model_path = os.path.join(os.path.dirname(__file__), 'image_detection', 'best_landmark_model_finetuned.pt')
        self.model = models.mobilenet_v3_large(weights=None)
        num_ftrs = self.model.classifier[3].in_features
        self.model.classifier[3] = nn.Linear(num_ftrs, len(self.class_names))
        
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(checkpoint)
        self.model = self.model.to(self.device)
        self.model.eval()
    
    def recognize_from_file(self, file):
        """从上传的文件识别地标"""
        try:
            image = Image.open(file.stream).convert('RGB')
            return self._predict(image)
        except:
            return "无法识别"
    
    def recognize_from_base64(self, base64_string):
        """从base64字符串识别地标"""
        try:
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            return self._predict(image)
        except:
            return "无法识别"
    
    def _predict(self, image):
        """执行预测"""
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
                    "landmark": landmark_name,
                    "confidence": round(confidence, 2)
                }
        except:
            return "无法识别"

# 创建全局识别器实例
recognizer = LandmarkAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "ok", "message": "地标识别API运行正常"})

@app.route('/recognize', methods=['POST'])
def recognize_landmark():
    """地标识别接口"""
    try:
        # 检查是否有文件上传
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "未选择文件"}), 400
            
            result = recognizer.recognize_from_file(file)
            
            if isinstance(result, dict):
                return jsonify({
                    "success": True,
                    "landmark": result["landmark"],
                    "confidence": result["confidence"]
                })
            else:
                return jsonify({
                    "success": True,
                    "landmark": result
                })
        
        # 检查是否有base64数据
        elif request.is_json and 'image_base64' in request.json:
            base64_string = request.json['image_base64']
            result = recognizer.recognize_from_base64(base64_string)
            
            if isinstance(result, dict):
                return jsonify({
                    "success": True,
                    "landmark": result["landmark"],
                    "confidence": result["confidence"]
                })
            else:
                return jsonify({
                    "success": True,
                    "landmark": result
                })
        
        else:
            return jsonify({"error": "请提供图片文件或base64编码的图片数据"}), 400
    
    except Exception as e:
        return jsonify({"error": f"识别失败: {str(e)}"}), 500

@app.route('/landmarks', methods=['GET'])
def get_supported_landmarks():
    """获取支持的地标列表"""
    landmarks = list(recognizer.chinese_names.values())
    return jsonify({
        "supported_landmarks": landmarks,
        "total_count": len(landmarks)
    })

if __name__ == '__main__':
    print("🚀 地标识别API服务启动")
    print("📍 健康检查: GET /health")
    print("🔍 地标识别: POST /recognize")
    print("📋 支持的地标: GET /landmarks")
    app.run(host='0.0.0.0', port=5000, debug=False) 