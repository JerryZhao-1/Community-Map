import requests
import base64
import logging
import time

logger = logging.getLogger(__name__)

class BaiduFacadeService:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.auth_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.recognize_url = "https://aip.baidubce.com/rest/2.0/realtime_search/v1/facade"
        self._access_token = None
        self._token_expiry_time = 0

    def get_access_token(self):
        # Check if the token is still valid
        if self._access_token and time.time() < self._token_expiry_time:
            return self._access_token

        if not self.api_key or not self.secret_key:
            logger.error("Baidu API Key or Secret Key not provided.")
            return None

        params = {"grant_type": "client_credentials", "client_id": self.api_key, "client_secret": self.secret_key}
        try:
            response = requests.post(self.auth_url, params=params, timeout=5)
            response.raise_for_status()
            result = response.json()
            self._access_token = result.get("access_token")
            expires_in = result.get("expires_in", 3600) - 60
            self._token_expiry_time = time.time() + expires_in
            logger.info("Successfully fetched and cached Baidu access_token.")
            return self._access_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Baidu access_token: {e}")
            return None

    def recognize(self, image_bytes):
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to get Baidu access_token, please check keys and network'}

        try:
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            params = {'access_token': access_token}
            data = {'image': img_base64}
            response = requests.post(self.recognize_url, headers=headers, params=params, data=data, timeout=10)
            response.raise_for_status()
            result = response.json()

            if "error_msg" in result:
                logger.error(f"Baidu API returned an error: {result['error_msg']}")
                return {'success': False, 'error': result['error_msg']}

            if result and 'result' in result and result.get('result_num', 0) > 0:
                first_match = result['result'][0]
                return {'success': True, 'landmark': first_match.get('brief', 'Unknown Facade'), 'confidence': first_match.get('probability', 0) * 100, 'source': 'Baidu Facade API'}
            else:
                return {'success': False, 'error': 'Baidu API did not recognize any facade'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Network exception when calling Baidu API: {e}")
            return {'success': False, 'error': f'Network exception with Baidu API: {e}'}
        except Exception as e:
            logger.error(f"Unknown exception processing Baidu API response: {e}")
            return {'success': False, 'error': f'Unknown exception with Baidu API response: {e}'}