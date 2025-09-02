from django.urls import path
from .views import LocationListCreateView, LocationDetailView, ImageUploadView, LocationListAPI
from . import views

urlpatterns = [
    path('locations/', LocationListCreateView.as_view(), name='location-list-create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('upload-image/', ImageUploadView.as_view(), name='upload-image'),
    path('', views.index, name='index'),
    path('api/recognize/', views.recognize_api_view, name='api_recognize'),
]

# from django.urls import path
# from . import views

# # 我们在这里只定义项目需要的 URL
# # 注意：原有的 upload-image/ 路径已被移除，因为它将被新的 api/recognize/ 取代
# urlpatterns = [
#     # 你原有的 API 路由
#     path('locations/', views.LocationListCreateView.as_view(), name='location-list-create'),
#     path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location-detail'),
    
#     # 我们新增的主页和识别 API 路由
#     path('', views.index, name='index'),
#     path('api/recognize/', views.recognize_api_view, name='api_recognize'),
# ]

