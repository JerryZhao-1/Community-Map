#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django集成示例代码
演示如何在Django项目中集成地标识别功能
"""

# ==== Django视图示例 ====

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.uploadedfile import InMemoryUploadedFile
import json
import logging
from .django_landmark_service import get_landmark_service

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def landmark_recognize_view(request):
    """Django视图：地标识别接口"""
    try:
        service = get_landmark_service()
        
        # 处理文件上传
        if 'image' in request.FILES:
            uploaded_file = request.FILES['image']
            result = service.recognize_from_django_file(uploaded_file)
            
        # 处理base64数据
        elif request.content_type == 'application/json':
            data = json.loads(request.body)
            if 'image_base64' in data:
                result = service.recognize_from_base64(data['image_base64'])
            else:
                return JsonResponse({'error': '缺少image_base64参数'}, status=400)
        else:
            return JsonResponse({'error': '请提供图片文件或base64数据'}, status=400)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"地标识别失败: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def landmark_list_view(request):
    """Django视图：获取支持的地标列表"""
    try:
        service = get_landmark_service()
        result = service.get_supported_landmarks()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"获取地标列表失败: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def landmark_health_view(request):
    """Django视图：健康检查"""
    try:
        service = get_landmark_service()
        result = service.health_check()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# ==== Django URLs配置示例 ====

"""
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/landmark/recognize/', views.landmark_recognize_view, name='landmark_recognize'),
    path('api/landmark/list/', views.landmark_list_view, name='landmark_list'),
    path('api/landmark/health/', views.landmark_health_view, name='landmark_health'),
]
"""

# ==== Django模型示例 ====

from django.db import models
from django.contrib.auth.models import User

class LandmarkRecognitionRecord(models.Model):
    """地标识别记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='landmark_images/', null=True, blank=True)
    recognized_landmark = models.CharField(max_length=200, null=True, blank=True)
    confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'landmark_recognition_records'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recognized_landmark} - {self.confidence:.2f}% ({self.created_at})"

# ==== Django表单示例 ====

from django import forms

class LandmarkRecognitionForm(forms.Form):
    """地标识别表单"""
    image = forms.ImageField(
        label='上传图片',
        help_text='支持jpg, jpeg, png, gif, bmp, tiff格式，最大16MB',
        required=True
    )
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # 检查文件大小
            if image.size > 16 * 1024 * 1024:  # 16MB
                raise forms.ValidationError('图片文件不能超过16MB')
            
            # 检查文件格式
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff']
            if image.content_type not in allowed_types:
                raise forms.ValidationError('不支持的图片格式')
        
        return image

# ==== Django管理界面示例 ====

from django.contrib import admin

@admin.register(LandmarkRecognitionRecord)
class LandmarkRecognitionRecordAdmin(admin.ModelAdmin):
    """地标识别记录管理界面"""
    list_display = ['id', 'user', 'recognized_landmark', 'confidence', 'success', 'created_at']
    list_filter = ['success', 'recognized_landmark', 'created_at']
    search_fields = ['recognized_landmark', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False  # 不允许手动添加记录

# ==== Django设置示例 ====

"""
# settings.py 中的相关配置

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 16 * 1024 * 1024  # 16MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 16 * 1024 * 1024  # 16MB

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'landmark_recognition.log',
        },
    },
    'loggers': {
        'django_landmark_service': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 应用配置
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'your_landmark_app',  # 您的地标识别应用
]
"""

# ==== 使用示例 ====

def example_usage():
    """使用示例"""
    from django_landmark_service import get_landmark_service
    
    # 初始化服务
    service = get_landmark_service()
    
    # 检查服务状态
    health = service.health_check()
    print(f"服务状态: {health}")
    
    # 从文件路径识别
    result = service.recognize_from_path('test_image.jpg')
    print(f"识别结果: {result}")
    
    # 获取支持的地标
    landmarks = service.get_supported_landmarks()
    print(f"支持的地标: {landmarks}") 