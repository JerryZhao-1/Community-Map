# 允许在未安装 dashscope 的环境下导入本模块（例如仅进行 Mock 测试）
try:
    import importlib
    dashscope = importlib.import_module('dashscope')
except Exception:  # pragma: no cover
    dashscope = None
import logging
import os
import json
import tempfile
from http import HTTPStatus
import re

logger = logging.getLogger(__name__)

class QwenVLService:
    def __init__(self):
        if dashscope is None:
            raise ImportError("dashscope 未安装，无法使用真实的 Qwen-VL 服务")
        api_key = os.environ.get("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("Qwen API Key not found in environment variables.")
        dashscope.api_key = api_key
        self.model = dashscope.MultiModalConversation

    def recognize(self, image_bytes, allowed_landmarks_cn=None):
        """Call Qwen-VL to recognize landmark from image bytes.

        Returns a dict like:
        { 'success': True, 'landmark': 'xxx', 'source': 'Qwen-VL', 'raw': optional_raw_text, 'other_name': '...' }
        or error dict on failure.
        """
        tmp_path = None
        try:
            # 使用安全的临时文件，避免并发冲突
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name

            local_file_path = f'file://{os.path.abspath(tmp_path)}'

            # 组织约束提示：优先在指定清单中选择，否则返回 other_name
            options_text = ''
            if allowed_landmarks_cn:
                options_text = "\n候选地标(中文，优先从中选择):\n- " + "\n- ".join(allowed_landmarks_cn)

            prompt_text = (
                "请分析图像并识别其中的地标(中文)。若该地标在以下候选清单中，请直接返回该清单里的标准名称；"
                "若完全不在清单中，请返回识别到的其他店名。\n"
                f"{options_text}\n\n"
                "请严格以 JSON 返回：\n"
                '{"landmark_name":"清单中匹配到的地标中文名或Not a landmark(若无)", '
                '"other_name":"当不在清单中时，你识别到的其他店名；若无请为空字符串"}'
                "\n不要包含任何解释、markdown 或多余文本。"
            )

            messages = [{
                'role': 'user',
                'content': [
                    {'image': local_file_path},
                    {'text': prompt_text}
                ]
            }]

            response = self.model.call(
                model='qwen-vl-max',
                messages=messages,
                vl_high_resolution_images=True
            )

            if response.status_code == HTTPStatus.OK:
                content = response.output.choices[0].message.content
                text_response = ""
                if isinstance(content, list) and len(content) > 0 and 'text' in content[0]:
                    text_response = content[0]['text']

                # 兼容 LLM 返回 ```json ... ``` 或混入说明文字的情况：去除代码围栏并提取首个 JSON 对象
                cleaned = text_response.strip()
                # 去除 Markdown 代码围栏
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```[a-zA-Z0-9]*\s*", "", cleaned)
                    cleaned = re.sub(r"\s*```$", "", cleaned)
                # 提取首个花括号包裹的 JSON 片段
                m = re.search(r"\{[\s\S]*\}", cleaned)
                if m:
                    cleaned = m.group(0)

                try:
                    data = json.loads(cleaned)
                    landmark_name = data.get("landmark_name")
                    other_name = data.get("other_name")

                    if allowed_landmarks_cn and landmark_name in (None, "Not a landmark", "") and other_name:
                        # 未匹配清单，但识别出了其他名称
                        return {'success': True, 'landmark': other_name, 'source': 'Qwen-VL', 'raw': text_response, 'other_name': other_name}

                    if not landmark_name or landmark_name == "Not a landmark":
                        return {'success': False, 'error': 'Qwen-VL 未识别到地标', 'raw': text_response, 'other_name': other_name}

                    return {'success': True, 'landmark': landmark_name, 'source': 'Qwen-VL', 'raw': text_response, 'other_name': other_name}
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response from Qwen-VL: {text_response}")
                    return {'success': False, 'error': 'Qwen-VL 返回解析失败', 'raw': text_response}

            else:
                error_message = f"Qwen-VL API 请求失败，状态码 {response.status_code}: {response.message}"
                logger.error(error_message)
                return {'success': False, 'error': error_message}

        except Exception as e:
            logger.error(f"调用 Qwen-VL 发生未知异常: {e}")
            return {'success': False, 'error': f'Qwen-VL 调用异常: {e}'}
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    # 清理失败不影响主流程
                    pass
