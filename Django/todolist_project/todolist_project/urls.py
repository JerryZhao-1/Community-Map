"""
URL configuration for todolist_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# todolist_project/urls.py
from django.contrib import admin
from django.urls import path, include # 确保 include 已导入

urlpatterns = [
    path('admin/', admin.site.urls),
    # 将所有来自根路径的请求都转发到 tasks 应用的 urls.py 文件中处理
    path('', include('tasks.urls')),
]
