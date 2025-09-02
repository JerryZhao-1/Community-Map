from .landmark_predictor import LandmarkPredictor
from .baidu_facade_service import BaiduFacadeService
import logging
import os

logger = logging.getLogger(__name__)

class LocalLandmarkService:
    _instance = None
    def __init__(self):
        try:
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
        LocalLandmarkService._instance = LocalLandmarkService()
    return LocalLandmarkService._instance

def _decide_best_result(local_res, baidu_res):
    local_success = local_res.get('success', False)
    baidu_success = baidu_res.get('success', False)
    if local_success and not baidu_success: return local_res
    if not local_success and baidu_success: return baidu_res
    if local_success and baidu_success:
        return local_res if local_res.get('confidence', 0) > baidu_res.get('confidence', 0) else baidu_res
    return {'success': False, 'error': 'Both recognition engines failed to produce a result'}

def recognize_image_hybrid(image_file, baidu_service_instance=None):
    """
    Recognizes an image using a hybrid approach (local model and optional Baidu API).

    Args:
        image_file: A file-like object containing the image data.
        baidu_service_instance: An optional initialized instance of BaiduFacadeService.

    Returns:
        A dictionary containing the recognition results.
    """
    try:
        image_file.seek(0)
        image_bytes = image_file.read()
        
        local_result = get_local_landmark_service().recognize(image_bytes)
        
        if baidu_service_instance:
            baidu_result = baidu_service_instance.recognize(image_bytes)
        else:
            baidu_result = {'success': False, 'error': 'Baidu service not configured'}

        final_result = _decide_best_result(local_result, baidu_result)
        
        return {'final_result': final_result, 'local_result': local_result, 'baidu_result': baidu_result}
        
    except Exception as e:
        logger.error(f"Critical error in recognition dispatcher: {e}")
        return {
            'final_result': {'success': False, 'error': 'Internal server error during image processing'},
            'local_result': {'success': False, 'error': str(e)},
            'baidu_result': {'success': False, 'error': str(e)}
        }

def get_landmark(image_path, baidu_api_key=None, baidu_secret_key=None):
    """
    Gets the landmark name from an image using a hybrid approach.

    Args:
        image_path: Path to the image file.
        baidu_api_key: Your Baidu API Key (optional).
        baidu_secret_key: Your Baidu Secret Key (optional).

    Returns:
        The name of the landmark as a string, or None if not found.
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found at: {image_path}")
        return None

    baidu_service = None
    if baidu_api_key and baidu_secret_key:
        baidu_service = BaiduFacadeService(api_key=baidu_api_key, secret_key=baidu_secret_key)

    with open(image_path, "rb") as f:
        results = recognize_image_hybrid(f, baidu_service_instance=baidu_service)
    
    final_result = results.get('final_result', {})
    if final_result.get('success'):
        return final_result.get('landmark')
    else:
        logger.warning(f"Could not determine landmark for {image_path}. Reason: {final_result.get('error')}")
        return None