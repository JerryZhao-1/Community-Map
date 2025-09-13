# 注：本地模型可选导入（无 torch 也可跑 Qwen-only 路径）
try:
    from .landmark_predictor import LandmarkPredictor  # 可选
except Exception:
    LandmarkPredictor = None
# 注：默认使用 Qwen 与本地模型；Baidu 模块非必需（保留 UNUSED 版本供将来启用）
try:
    from .baidu_facade_service import BaiduFacadeService  # 可选
except Exception:  # pragma: no cover - 不影响 Qwen-only 路径
    BaiduFacadeService = None
from .qwen_vl_service import QwenVLService
from .constants import ALLOWED_LANDMARKS_CN
import logging
import os
import threading

logger = logging.getLogger(__name__)

class LocalLandmarkService:
    _instance = None
    _lock = threading.Lock()
    def __init__(self):
        try:
            if LandmarkPredictor is None:
                logger.warning("LandmarkPredictor 未可用（可能未安装 torch），本地模型将不可用")
                self.model = None
            else:
                self.model = LandmarkPredictor()
                logger.info("Local landmark recognition model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load local landmark recognition model: {e}")
            self.model = None

    def recognize(self, image_bytes):
        if not self.model:
            return {'success': False, 'error': 'Local model not loaded, check server logs'}
        
        try:
            landmark_name, confidence = self.model.predict(image_bytes)
            return {
                'success': True, 
                'landmark': landmark_name, 
                'confidence': confidence, 
                'source': 'Local Landmark Model'
            }
        except Exception as e:
            logger.error(f"Error during local model prediction: {e}")
            return {'success': False, 'error': f'Local model prediction failed: {e}'}

def get_local_landmark_service():
    if LocalLandmarkService._instance is None:
        with LocalLandmarkService._lock:
            if LocalLandmarkService._instance is None:
                LocalLandmarkService._instance = LocalLandmarkService()
    return LocalLandmarkService._instance

def _decide_best_result(local_res, baidu_res, qwen_res):
    local_success = local_res.get('success', False)
    baidu_success = baidu_res.get('success', False)
    qwen_success = qwen_res.get('success', False)

    if local_success:
        return local_res
    if qwen_success:
        return qwen_res
    if baidu_success:
        return baidu_res
        
    return {'success': False, 'error': 'All recognition engines failed to produce a result'}

def recognize_image_hybrid(image_file, baidu_service_instance=None, qwen_service_instance=None):
    """
    混合识别：本地模型 + （可选）Baidu + （可选）Qwen-VL。

    Args:
        image_file: A file-like object containing the image data.
        baidu_service_instance: 可选 BaiduFacadeService 实例（未提供或模块不可用时将跳过）。
        qwen_service_instance: An optional initialized instance of QwenVLService.

    Returns:
        A dictionary containing the recognition results.
    """
    try:
        image_file.seek(0)
        image_bytes = image_file.read()

        local_result = get_local_landmark_service().recognize(image_bytes)

        if baidu_service_instance and BaiduFacadeService is not None:
            baidu_result = baidu_service_instance.recognize(image_bytes)
        else:
            baidu_result = {'success': False, 'error': 'Baidu service not configured'}

        if qwen_service_instance:
            qwen_result = qwen_service_instance.recognize(image_bytes)
        else:
            qwen_result = {'success': False, 'error': 'Qwen-VL service not configured'}

        final_result = _decide_best_result(local_result, baidu_result, qwen_result)

        return {'final_result': final_result, 'local_result': local_result, 'baidu_result': baidu_result, 'qwen_result': qwen_result}

    except Exception as e:
        logger.error(f"Critical error in recognition dispatcher: {e}")
        return {
            'final_result': {'success': False, 'error': 'Internal server error during image processing'},
            'local_result': {'success': False, 'error': str(e)},
            'baidu_result': {'success': False, 'error': str(e)},
            'qwen_result': {'success': False, 'error': str(e)}
        }

def get_landmark(image_path):
    """
    默认模式：同时使用 Qwen 与本地模型，最终仅返回 {'success', 'landmark'}。

    规则：
    - 若两者都成功但不一致：以 Qwen 为准；
    - 仅一方成功：取成功的一方；
    - 均失败：success=False, landmark=None。
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found at: {image_path}")
        return {'success': False, 'landmark': None}

    # 读入一次字节，供两路使用
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
    except Exception as e:
        logger.error(f"Failed to read image: {e}")
        return {'success': False, 'landmark': None}

    # 调用 Qwen
    qwen_res = {'success': False}
    if os.environ.get("DASHSCOPE_API_KEY"):
        try:
            qwen_service = QwenVLService()
            qwen_res = qwen_service.recognize(image_bytes, allowed_landmarks_cn=ALLOWED_LANDMARKS_CN)
        except Exception as e:
            logger.warning(f"Qwen combined call failed: {e}")

    # 调用本地模型
    local_res = get_local_landmark_service().recognize(image_bytes)

    # 决策
    q_ok, l_ok = qwen_res.get('success', False), local_res.get('success', False)
    q_name, l_name = qwen_res.get('landmark'), local_res.get('landmark')

    if q_ok and l_ok:
        # 冲突以 Qwen 为准
        final_name = q_name if q_name else l_name
        return {'success': True, 'landmark': final_name}
    if q_ok:
        return {'success': True, 'landmark': q_name}
    if l_ok:
        return {'success': True, 'landmark': l_name}
    return {'success': False, 'landmark': None}


# =====================  Qwen-Only 简化路径  =====================
def recognize_image_qwen(image_file, qwen_service_instance=None):
    """
    仅使用 Qwen-VL 进行识别。

    Args:
        image_file: A file-like object containing the image data.
        qwen_service_instance: 可选的 QwenVLService 实例；若未提供则根据环境变量自动创建。

    Returns:
        dict: {'success': bool, 'landmark': str?, 'source': 'Qwen-VL', 'raw': str? , 'error': str?}
    """
    try:
        image_file.seek(0)
        image_bytes = image_file.read()

        if qwen_service_instance is None:
            if not os.environ.get("DASHSCOPE_API_KEY"):
                return {'success': False, 'error': '未配置 DASHSCOPE_API_KEY'}
            qwen_service_instance = QwenVLService()

        qwen_result = qwen_service_instance.recognize(image_bytes, allowed_landmarks_cn=ALLOWED_LANDMARKS_CN)
        return qwen_result
    except Exception as e:
        logger.error(f"Qwen-only 识别异常: {e}")
        return {'success': False, 'error': f'Qwen-only 识别异常: {e}'}


def get_landmark_qwen(image_path, return_details=False):
    """
    仅用 Qwen-VL 识别地标。

    Args:
        image_path: 图片路径
        return_details: 测试阶段若为 True，返回包含原始响应在内的详细信息；否则仅返回地标名字符串

    Returns:
        - 若 return_details=False: str | None （地标名或 None）
        - 若 return_details=True: dict {'success', 'landmark'?, 'raw'?, 'error'?}
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found at: {image_path}")
        return None if not return_details else {'success': False, 'error': 'Image file not found'}

    with open(image_path, 'rb') as f:
        res = recognize_image_qwen(f)

    if return_details:
        return res

    if res.get('success'):
        return res.get('landmark')
    return None


def get_landmarks_qwen_in_dir(dir_path, return_details=False, extensions=("jpg", "jpeg", "png", "bmp", "webp")):
    """
    批量：对目录中的图片逐一使用 Qwen-VL 识别。

    Args:
        dir_path: 图片所在目录
        return_details: 同 get_landmark_qwen
        extensions: 允许的扩展名集合（小写，无点）

    Returns:
        list[dict]: [{ 'path': str, 'landmark': str|None }] 或
                    [{ 'path': str, 'result': dict }] 当 return_details=True
    """
    if not os.path.isdir(dir_path):
        logger.error(f"Directory not found: {dir_path}")
        return []

    results = []
    try:
        for name in sorted(os.listdir(dir_path)):
            fpath = os.path.join(dir_path, name)
            if not os.path.isfile(fpath):
                continue
            ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
            if extensions and ext not in extensions:
                continue

            if return_details:
                result = get_landmark_qwen(fpath, return_details=True)
                results.append({'path': fpath, 'result': result})
            else:
                landmark = get_landmark_qwen(fpath, return_details=False)
                results.append({'path': fpath, 'landmark': landmark})
    except Exception as e:
        logger.error(f"Batch Qwen recognition failed: {e}")

    return results


def get_landmark_minimal(image_path):
    """
    返回极简结果：仅 {'success': bool, 'landmark': str|None}

    规则：
    - 优先使用 Qwen 结果（若配置了 DASHSCOPE_API_KEY 且调用成功）。
    - 若 Qwen 不可用或失败，则使用本地模型结果（如可用）。
    - 若两者都失败：success=False, landmark=None。
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found at: {image_path}")
        return {'success': False, 'landmark': None}

    qwen_ok = False
    qwen_landmark = None

    # Qwen 优先
    try:
        with open(image_path, 'rb') as f:
            if os.environ.get("DASHSCOPE_API_KEY"):
                qwen_service = QwenVLService()
                qres = qwen_service.recognize(f.read(), allowed_landmarks_cn=ALLOWED_LANDMARKS_CN)
                if qres.get('success'):
                    qwen_ok = True
                    qwen_landmark = qres.get('landmark')
    except Exception as e:
        logger.warning(f"Qwen minimal path failed: {e}")

    if qwen_ok:
        return {'success': True, 'landmark': qwen_landmark}

    # 本地备选
    try:
        with open(image_path, 'rb') as f:
            local_res = get_local_landmark_service().recognize(f.read())
            if local_res.get('success'):
                return {'success': True, 'landmark': local_res.get('landmark')}
    except Exception as e:
        logger.warning(f"Local minimal path failed: {e}")

    return {'success': False, 'landmark': None}