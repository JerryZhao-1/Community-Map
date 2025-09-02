from .image_detection.landmark_predictor import LandmarkPredictor
from .baidu_facade_service import get_baidu_facade_service
import logging

logger = logging.getLogger(__name__)

class LocalLandmarkService:
    _instance = None
    def __init__(self):
        try:
            self.model = LandmarkPredictor()
            logger.info("本地地标识别模型加载成功。")
        except Exception as e:
            logger.error(f"本地地标识别模型加载失败: {e}")
            self.model = None

    def recognize(self, image_bytes):
        if not self.model:
            return {'success': False, 'error': '本地模型未能成功加载，请检查服务器日志'}
        
        # --- 这是关键的加固代码 ---
        try:
            landmark_name, confidence = self.model.predict(image_bytes)
            return {
                'success': True, 
                'landmark': landmark_name, 
                'confidence': confidence, 
                'source': 'Local Landmark Model'
            }
        except Exception as e:
            # 如果模型预测时出错，捕获异常并返回清晰的JSON错误
            logger.error(f"本地模型在预测时出错: {e}")
            return {'success': False, 'error': f'本地模型预测失败: {e}'}

def get_local_landmark_service():
    if LocalLandmarkService._instance is None:
        LocalLandmarkService._instance = LocalLandmarkService()
    return LocalLandmarkService._instance

def _decide_best_result(local_res, baidu_res):
    local_success = local_res.get('success', False)
    baidu_success = baidu_res.get('success', False)
    if local_success and not baidu_success: return local_res
    if not local_success and baidu_success: return baidu_res
    if local_success and baidu_success:
        return local_res if local_res.get('confidence', 0) > baidu_res.get('confidence', 0) else baidu_res
    return {'success': False, 'error': '两个识别引擎均未能识别出结果'}

def recognize_image_hybrid(image_file):
    try:
        image_file.seek(0)
        image_bytes = image_file.read()
        local_result = get_local_landmark_service().recognize(image_bytes)
        baidu_result = get_baidu_facade_service().recognize(image_bytes)
        final_result = _decide_best_result(local_result, baidu_result)
        return {'final_result': final_result, 'local_result': local_result, 'baidu_result': baidu_result}
    except Exception as e:
        logger.error(f"图片识别调度中心发生严重错误: {e}")
        return {
            'final_result': {'success': False, 'error': '处理图片时发生内部严重错误'},
            'local_result': {'success': False, 'error': str(e)},
            'baidu_result': {'success': False, 'error': str(e)}
        }