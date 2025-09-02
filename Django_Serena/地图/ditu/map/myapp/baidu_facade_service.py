import requests
import base64
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class BaiduFacadeService:
    _instance = None
    def __init__(self):
        self.api_key = getattr(settings, 'BAIDU_API_KEY', None)
        self.secret_key = getattr(settings, 'BAIDU_SECRET_KEY', None)
        self.auth_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.recognize_url = "https://aip.baidubce.com/rest/2.0/realtime_search/v1/facade"

    def get_access_token(self):
        token = cache.get('baidu_access_token')
        if token: return token
        if not self.api_key or not self.secret_key:
            logger.error("百度云 API Key 或 Secret Key 未在 settings.py 中配置。")
            return None
        params = {"grant_type": "client_credentials", "client_id": self.api_key, "client_secret": self.secret_key}
        try:
            response = requests.post(self.auth_url, params=params, timeout=5) # 增加超时
            response.raise_for_status()
            result = response.json()
            token = result.get("access_token")
            expires_in = result.get("expires_in", 3600) - 60
            cache.set('baidu_access_token', token, timeout=expires_in)
            logger.info("成功获取并缓存了百度云 access_token。")
            return token
        except requests.exceptions.RequestException as e:
            logger.error(f"获取百度云 access_token 失败: {e}")
            return None

    def recognize(self, image_bytes):
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'error': '获取百度云 access_token 失败，请检查密钥和网络'}
        
        # --- 这是关键的加固代码 ---
        try:
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            params = {'access_token': access_token}
            data = {'image': img_base64}
            response = requests.post(self.recognize_url, headers=headers, params=params, data=data, timeout=10) # 增加超时
            response.raise_for_status()
            result = response.json()

            if "error_msg" in result:
                logger.error(f"百度云 API 返回错误: {result['error_msg']}")
                return {'success': False, 'error': result['error_msg']}
            
            if result and 'result' in result and result.get('result_num', 0) > 0:
                first_match = result['result'][0]
                return {'success': True, 'landmark': first_match.get('brief', '未知门脸'), 'confidence': first_match.get('probability', 0) * 100, 'source': 'Baidu Facade API'}
            else:
                return {'success': False, 'error': '百度云API未能识别到任何门脸'}
        except requests.exceptions.RequestException as e:
            logger.error(f"调用百度云 API 时发生网络异常: {e}")
            return {'success': False, 'error': f'调用百度云API时网络异常: {e}'}
        except Exception as e:
            logger.error(f"处理百度云 API 响应时发生未知异常: {e}")
            return {'success': False, 'error': f'处理百度云API响应时发生未知异常: {e}'}

def get_baidu_facade_service():
    if BaiduFacadeService._instance is None:
        BaiduFacadeService._instance = BaiduFacadeService()
    return BaiduFacadeService._instance