# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 网站根路径 ('/')，显示所有任务
    path('', views.task_list, name='task_list'),
    # 用于创建任务的路径 ('/create/')
    path('create/', views.task_create, name='task_create'),
    # 用于更新任务状态的路径，例如 '/update/5/'
    path('update/<int:task_id>/', views.task_update, name='task_update'),
    # 用于删除任务的路径，例如 '/delete/5/'
    path('delete/<int:task_id>/', views.task_delete, name='task_delete'),
]