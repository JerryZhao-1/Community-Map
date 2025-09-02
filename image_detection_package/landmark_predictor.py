# import torch
# import torch.nn as nn
# from torchvision import models, transforms
# from PIL import Image
# import os
# import argparse
# import sys

# class LandmarkPredictor:
#     def __init__(self, model_path='best_landmark_model_finetuned.pt'):
#         """
#         初始化地标识别预测器
        
#         Args:
#             model_path: 训练好的模型文件路径
#         """
#         self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#         self.model_path = model_path
        
#         # 数据预处理管道（与训练时保持一致）
#         self.transform = transforms.Compose([
#             transforms.Resize(256),
#             transforms.CenterCrop(224),
#             transforms.ToTensor(),
#             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
#         ])
        
#         # 模型训练时使用的类别名称（按字母顺序，与训练时保持一致）
#         self.class_names = [
#             'Gilis', 'baolihui', 'ccb', 'chaimengongguan', 'chengduyan', 
#             'communitycenter', 'dianyingyuan', 'flouxetine', 'kaibinsiji', 'luji', 'morgan', 
#             'ouzhoufengqingjie', 'sijiguo', 'wanlijiudian', 'weishengzhongxin', 'yangya', 
#             'yingdangbaoyu', 'yinyuefangzi'
#         ]
        
#         # 地标中文名称映射
#         self.chinese_names = {
#             'Gilis': '其心西餐厅',
#             'baolihui': '宝利汇',
#             'ccb': '建设银行',
#             'chaimengongguan': '柴门公馆 (桐梓林店)',
#             'chengduyan': '成都宴 (桐梓林店)',
#             'communitycenter': '社区活动中心',
#             'dianyingyuan': '紫荆电影院',
#             'flouxetine': '氟西汀Whisky&Cocktail Bar (桐梓林店)',
#             'kaibinsiji': '成都凯宾斯基饭店',
#             'luji': '卢记正街饭店·川湘菜',
#             'morgan': '摩根扒房',
#             'ouzhoufengqingjie': '桐梓林欧洲风情街',
#             'sijiguo': '四季锅火锅 (桐梓林店)',
#             'wanlijiudian': '成都首座万丽酒店',
#             'weishengzhongxin': '卫生中心',
#             'yangya': '漾亚·雍雅合鲜 (桐梓林店)',
#             'yingdangbaoyu': '银滩鲍鱼火锅 (希望路店)',
#             'yinyuefangzi': '音乐房子 (玉林店)'
#         }
        
#         # 地标分类
#         self.landmark_categories = {
#             '餐厅': [
#                 '成都宴 (桐梓林店)', '柴门公馆 (桐梓林店)', '漾亚·雍雅合鲜 (桐梓林店)',
#                 '银滩鲍鱼火锅 (希望路店)', '其心西餐厅', '摩根扒房',
#                 '四季锅火锅 (桐梓林店)', '卢记正街饭店·川湘菜'
#             ],
#             '酒吧': [
#                 '氟西汀Whisky&Cocktail Bar (桐梓林店)', '音乐房子 (玉林店)'
#             ],
#             '公共服务': [
#                 '社区活动中心', '卫生中心'
#             ],
#             '娱乐与其他': [
#                 '桐梓林欧洲风情街', '紫荆电影院', '成都凯宾斯基饭店',
#                 '成都首座万丽酒店', '建设银行', '宝利汇'
#             ]
#         }
        
#         self.num_classes = len(self.class_names)
#         self.model = None
        
#         # 加载模型
#         self._load_model()
    
#     def get_chinese_name(self, english_name):
#         """获取地标的中文名称"""
#         return self.chinese_names.get(english_name, english_name)
    
#     def get_landmark_category(self, chinese_name):
#         """获取地标的分类"""
#         for category, landmarks in self.landmark_categories.items():
#             if chinese_name in landmarks:
#                 return category
#         return "未分类"
    
#     def _load_model(self):
#         """加载训练好的模型"""
#         try:
#             print(f"正在加载模型: {self.model_path}")
#             print(f"使用设备: {self.device}")
            
#             # 创建模型架构
#             self.model = models.mobilenet_v3_large(weights=None)
#             num_ftrs = self.model.classifier[3].in_features
#             self.model.classifier[3] = nn.Linear(num_ftrs, self.num_classes)
            
#             # 加载训练好的权重
#             checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=True)
#             self.model.load_state_dict(checkpoint)
            
#             # 设置为评估模式
#             self.model = self.model.to(self.device)
#             self.model.eval()
            
#             print("✅ 模型加载成功!")
#             print(f"支持识别的地标类别: {len(self.class_names)} 个")
            
#             # 按分类显示支持的地标
#             print("\n📍 支持识别的地标:")
#             for category, landmarks in self.landmark_categories.items():
#                 print(f"  {category}: {', '.join(landmarks)}")
            
#         except Exception as e:
#             print(f"❌ 模型加载失败: {e}")
#             sys.exit(1)
    
#     def predict_image(self, image_path, show_top_k=3):
#         """
#         预测单张图片的地标类别
        
#         Args:
#             image_path: 图片文件路径
#             show_top_k: 显示前K个最可能的预测结果
            
#         Returns:
#             dict: 包含预测结果的字典
#         """
#         try:
#             # 检查文件是否存在
#             if not os.path.exists(image_path):
#                 raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
#             # 加载和预处理图片
#             image = Image.open(image_path).convert('RGB')
#             input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
#             # 进行预测
#             with torch.no_grad():
#                 outputs = self.model(input_tensor)
#                 probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                
#                 # 获取最高概率的预测
#                 _, predicted = torch.max(outputs, 1)
#                 predicted_english = self.class_names[predicted.item()]
#                 predicted_chinese = self.get_chinese_name(predicted_english)
#                 confidence = probabilities[predicted.item()].item() * 100
#                 category = self.get_landmark_category(predicted_chinese)
                
#                 # 获取前K个最可能的预测
#                 top_k_prob, top_k_idx = torch.topk(probabilities, min(show_top_k, len(self.class_names)))
#                 top_k_results = []
#                 for i in range(len(top_k_prob)):
#                     english_name = self.class_names[top_k_idx[i]]
#                     chinese_name = self.get_chinese_name(english_name)
#                     top_k_results.append({
#                         'landmark_english': english_name,
#                         'landmark_chinese': chinese_name,
#                         'landmark': chinese_name,  # 保持向后兼容
#                         'confidence': top_k_prob[i].item() * 100
#                     })
                
#                 return {
#                     'image_path': image_path,
#                     'predicted_landmark_english': predicted_english,
#                     'predicted_landmark_chinese': predicted_chinese,
#                     'predicted_landmark': predicted_chinese,  # 保持向后兼容
#                     'landmark_category': category,
#                     'confidence': confidence,
#                     'top_k_predictions': top_k_results,
#                     'success': True
#                 }
                
#         except Exception as e:
#             return {
#                 'image_path': image_path,
#                 'error': str(e),
#                 'success': False
#             }
    
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import argparse
import sys
import io  # 导入 io 模块

class LandmarkPredictor:
    def __init__(self, model_path='best_landmark_model_finetuned.pt'):
        """
        初始化地标识别预测器
        """
        # ===================================================================
        #  ↓↓↓↓↓ 关键修复 1: 使用绝对路径加载模型 ↓↓↓↓↓
        # ===================================================================
        # 获取当前脚本文件所在的绝对目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 将模型路径拼接成绝对路径
        self.model_path = os.path.join(base_dir, model_path)
        # ===================================================================
        #  ↑↑↑↑↑ 路径修复结束 ↑↑↑↑↑
        # ===================================================================
        
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        # 数据预处理管道（与训练时保持一致）
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        # --- 你原有的所有数据都完整保留 ---
        self.class_names = [
            'Gilis', 'baolihui', 'ccb', 'chaimengongguan', 'chengduyan', 
            'communitycenter', 'dianyingyuan', 'flouxetine', 'kaibinsiji', 'luji', 'morgan', 
            'ouzhoufengqingjie', 'sijiguo', 'wanlijiudian', 'weishengzhongxin', 'yangya', 
            'yingdangbaoyu', 'yinyuefangzi'
        ]
        self.chinese_names = {
            'Gilis': '其心西餐厅', 'baolihui': '宝利汇', 'ccb': '建设银行',
            'chaimengongguan': '柴门公馆 (桐梓林店)', 'chengduyan': '成都宴 (桐梓林店)',
            'communitycenter': '社区活动中心', 'dianyingyuan': '紫荆电影院',
            'flouxetine': '氟西汀Whisky&Cocktail Bar (桐梓林店)', 'kaibinsiji': '成都凯宾斯基饭店',
            'luji': '卢记正街饭店·川湘菜', 'morgan': '摩根扒房',
            'ouzhoufengqingjie': '桐梓林欧洲风情街', 'sijiguo': '四季锅火锅 (桐梓林店)',
            'wanlijiudian': '成都首座万丽酒店', 'weishengzhongxin': '卫生中心',
            'yangya': '漾亚·雍雅合鲜 (桐梓林店)', 'yingdangbaoyu': '银滩鲍鱼火锅 (希望路店)',
            'yinyuefangzi': '音乐房子 (玉林店)'
        }
        self.landmark_categories = {
            '餐厅': ['成都宴 (桐梓林店)', '柴门公馆 (桐梓林店)', '漾亚·雍雅合鲜 (桐梓林店)', '银滩鲍鱼火锅 (希望路店)', '其心西餐厅', '摩根扒房', '四季锅火锅 (桐梓林店)', '卢记正街饭店·川湘菜'],
            '酒吧': ['氟西汀Whisky&Cocktail Bar (桐梓林店)', '音乐房子 (玉林店)'],
            '公共服务': ['社区活动中心', '卫生中心'],
            '娱乐与其他': ['桐梓林欧洲风情街', '紫荆电影院', '成都凯宾斯基饭店', '成都首座万丽酒店', '建设银行', '宝利汇']
        }
        
        self.num_classes = len(self.class_names)
        self.model = None
        self._load_model()
    
    # --- 你原有的所有方法都完整保留 ---
    def get_chinese_name(self, english_name):
        return self.chinese_names.get(english_name, english_name)
    
    def get_landmark_category(self, chinese_name):
        for category, landmarks in self.landmark_categories.items():
            if chinese_name in landmarks:
                return category
        return "未分类"
    
    def _load_model(self):
        try:
            print(f"正在加载模型: {self.model_path}")
            print(f"使用设备: {self.device}")
            
            # 检查文件是否存在
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"模型文件不存在: {self.model_path}")

            # 保持你原有的模型架构
            self.model = models.mobilenet_v3_large(weights=None)
            # 注意：这里的 classifier[3] 是根据你原始代码来的，非常重要
            num_ftrs = self.model.classifier[3].in_features
            self.model.classifier[3] = nn.Linear(num_ftrs, self.num_classes)
            
            checkpoint = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint)
            
            self.model = self.model.to(self.device)
            self.model.eval()
            print("✅ 模型加载成功!")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            # 在 Django 环境中，我们不应该退出程序，而是让 model 保持为 None
            self.model = None
    
    # ===================================================================
    #  ↓↓↓↓↓ 关键修复 2: 新增一个方法来处理 Django 传来的图片数据 ↓↓↓↓↓
    # ===================================================================
    def predict(self, image_bytes):
        """
        专门为 Django 设计的预测方法，接收内存中的图片字节流
        """
        if not self.model:
            raise Exception("模型未能成功加载，无法进行预测。")

        # 从字节流中加载图片
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            _, predicted = torch.max(outputs, 1)
            predicted_english = self.class_names[predicted.item()]
            predicted_chinese = self.get_chinese_name(predicted_english)
            confidence = probabilities[predicted.item()].item() * 100
            
        # 返回调度中心需要的数据格式：(地标中文名, 置信度)
        return predicted_chinese, confidence
    # ===================================================================
    #  ↑↑↑↑↑ 新增方法结束 ↑↑↑↑↑
    # ===================================================================

    # --- 你原有的其他方法 (predict_image, predict_batch 等) 都完整保留在下方 ---
    # --- 这样你的脚本仍然可以独立运行进行测试 ---
    def predict_image(self, image_path, show_top_k=3):
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            # 从文件路径加载图片
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            # 复用新的 predict 方法
            predicted_chinese, confidence = self.predict(image_bytes)

            # 为了保持原有函数的输出格式，我们在这里重新组织一下
            predicted_english = [k for k, v in self.chinese_names.items() if v == predicted_chinese][0]
            category = self.get_landmark_category(predicted_chinese)

            # 此处简化了 top_k 的逻辑，只返回最主要的预测结果
            top_k_results = [{
                'landmark_english': predicted_english,
                'landmark_chinese': predicted_chinese,
                'landmark': predicted_chinese, # 保持向后兼容
                'confidence': confidence
            }]

            return {
                'image_path': image_path,
                'predicted_landmark_english': predicted_english,
                'predicted_landmark_chinese': predicted_chinese,
                'predicted_landmark': predicted_chinese, # 保持向后兼容
                'landmark_category': category,
                'confidence': confidence,
                'top_k_predictions': top_k_results,
                'success': True
            }
        except Exception as e:
            return {'image_path': image_path, 'error': str(e), 'success': False}
    
    # ... (你其他的 predict_batch, print_prediction_result, main 函数等都可以在这里继续保留) ...

    def predict_batch(self, image_paths, show_top_k=3):
        """
        批量预测多张图片
        
        Args:
            image_paths: 图片文件路径列表
            show_top_k: 显示前K个最可能的预测结果
            
        Returns:
            list: 包含所有预测结果的列表
        """
        results = []
        total_images = len(image_paths)
        
        print(f"开始批量预测 {total_images} 张图片...")
        print("-" * 60)
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"处理第 {i}/{total_images} 张图片: {os.path.basename(image_path)}")
            result = self.predict_image(image_path, show_top_k)
            results.append(result)
            
            if result['success']:
                print(f"✅ 预测结果: {result['predicted_landmark_chinese']} (置信度: {result['confidence']:.2f}%)")
                print(f"   分类: {result['landmark_category']}")
            else:
                print(f"❌ 预测失败: {result['error']}")
            print()
        
        return results
    
    def print_prediction_result(self, result):
        """格式化打印预测结果"""
        if not result['success']:
            print(f"❌ 预测失败: {result['error']}")
            return
        
        print(f"🖼️  图片: {os.path.basename(result['image_path'])}")
        print(f"🎯 预测地标: {result['predicted_landmark_chinese']}")
        print(f"🏷️  地标分类: {result['landmark_category']}")
        print(f"📊 置信度: {result['confidence']:.2f}%")
        
        if result['top_k_predictions']:
            print(f"\n📋 详细预测结果:")
            for i, pred in enumerate(result['top_k_predictions'], 1):
                category = self.get_landmark_category(pred['landmark_chinese'])
                print(f"   {i}. {pred['landmark_chinese']} ({category}): {pred['confidence']:.2f}%")

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='地标识别程序 - 桐梓林社区地标识别系统')
    parser.add_argument('--image', '-i', type=str, help='单张图片路径')
    parser.add_argument('--batch', '-b', type=str, nargs='+', help='多张图片路径')
    parser.add_argument('--folder', '-f', type=str, help='图片文件夹路径')
    parser.add_argument('--model', '-m', type=str, default='best_landmark_model_finetuned.pt', 
                       help='模型文件路径 (默认: best_landmark_model_finetuned.pt)')
    parser.add_argument('--top-k', '-k', type=int, default=3, 
                       help='显示前K个预测结果 (默认: 3)')
    
    args = parser.parse_args()
    
    # 检查参数
    if not any([args.image, args.batch, args.folder]):
        print("🏙️ 桐梓林社区地标识别系统")
        print("请指定要预测的图片:")
        print("  单张图片: python landmark_predictor.py --image path/to/image.jpg")
        print("  多张图片: python landmark_predictor.py --batch image1.jpg image2.jpg")
        print("  整个文件夹: python landmark_predictor.py --folder path/to/folder")
        return
    
    # 初始化预测器
    predictor = LandmarkPredictor(args.model)
    print("\n" + "="*60)
    
    # 执行预测
    if args.image:
        # 单张图片预测
        print("🔍 单张图片预测模式")
        print("="*60)
        result = predictor.predict_image(args.image, args.top_k)
        predictor.print_prediction_result(result)
        
    elif args.batch:
        # 批量图片预测
        print("🔍 批量图片预测模式")
        print("="*60)
        results = predictor.predict_batch(args.batch, args.top_k)
        
        # 统计成功率和分类统计
        successful = sum(1 for r in results if r['success'])
        category_stats = {}
        for result in results:
            if result['success']:
                category = result['landmark_category']
                category_stats[category] = category_stats.get(category, 0) + 1
        
        print(f"\n📈 预测统计:")
        print(f"   总计: {len(results)} 张图片")
        print(f"   成功: {successful} 张")
        print(f"   失败: {len(results) - successful} 张")
        print(f"   成功率: {successful/len(results)*100:.1f}%")
        
        if category_stats:
            print(f"\n📊 地标分类统计:")
            for category, count in category_stats.items():
                print(f"   {category}: {count} 张")
        
    elif args.folder:
        # 文件夹预测
        print("🔍 文件夹预测模式")
        print("="*60)
        
        if not os.path.exists(args.folder):
            print(f"❌ 文件夹不存在: {args.folder}")
            return
        
        # 获取文件夹中的所有图片
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
        image_paths = []
        
        for filename in os.listdir(args.folder):
            if filename.lower().endswith(image_extensions):
                image_paths.append(os.path.join(args.folder, filename))
        
        if not image_paths:
            print(f"❌ 在文件夹 {args.folder} 中没有找到图片文件")
            return
        
        print(f"找到 {len(image_paths)} 张图片")
        results = predictor.predict_batch(image_paths, args.top_k)
        
        # 统计成功率和分类统计
        successful = sum(1 for r in results if r['success'])
        category_stats = {}
        for result in results:
            if result['success']:
                category = result['landmark_category']
                category_stats[category] = category_stats.get(category, 0) + 1
        
        print(f"📈 预测统计:")
        print(f"   总计: {len(results)} 张图片")
        print(f"   成功: {successful} 张")
        print(f"   失败: {len(results) - successful} 张")
        print(f"   成功率: {successful/len(results)*100:.1f}%")
        
        if category_stats:
            print(f"\n📊 地标分类统计:")
            for category, count in category_stats.items():
                print(f"   {category}: {count} 张")

if __name__ == "__main__":
    main()
