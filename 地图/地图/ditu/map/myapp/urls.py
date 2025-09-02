from django.urls import path
from .views import LocationListCreateView, LocationDetailView, ImageUploadView, LocationListAPI

urlpatterns = [
    path('locations/', LocationListCreateView.as_view(), name='location-list-create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('upload-image/', ImageUploadView.as_view(), name='upload-image'),
    path('locations/', LocationListAPI.as_view(), name='location-list')
]