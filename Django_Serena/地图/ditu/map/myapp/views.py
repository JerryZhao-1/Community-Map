from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from django.conf import settings
from .models import Location
from .serializers import LocationSerializer
from django.shortcuts import render

from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from .recognition_dispatcher import recognize_image_hybrid
import logging

logger = logging.getLogger(__name__)

import os
import requests
import base64
# import paddlehub as hub

def index(request):
    return render(request, 'index.html')
# ====================================

class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class LocationListAPI(APIView):
    def get(self, request):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImageUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'error': 'No image uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        # 保存图片到media/location_images/
        save_path = os.path.join(settings.MEDIA_ROOT, 'location_images', file_obj.name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        image_url = settings.MEDIA_URL + 'location_images/' + file_obj.name
        result = recognize_image(save_path)
        return Response({'image_url': image_url, 'recognition': result})


def recognize_image(image_path):
    # 
    return "test"


# @csrf_exempt
def recognize_api_view(request):
    """
    处理图片识别的API请求
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '只接受POST请求'}, status=405)
    try:
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return JsonResponse({'success': False, 'error': '没有找到上传的图片文件'}, status=400)
        
        comprehensive_result = recognize_image_hybrid(uploaded_file)
        return JsonResponse(comprehensive_result)
    
    except Exception as e:
        logger.error(f"识别API视图出错: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

