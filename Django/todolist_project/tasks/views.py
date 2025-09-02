# tasks/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task

# 视图函数：显示所有任务
def task_list(request):
    tasks = Task.objects.all()
    # 将查询到的任务数据传递给模板
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

# 视图函数：创建新任务
def task_create(request):
    # 只处理 POST 请求
    if request.method == 'POST':
        # 从表单的 POST 请求中获取 'title' 数据
        title = request.POST.get('title', '').strip()
        if title: # 确保标题不为空
            Task.objects.create(title=title)
    # 操作完成后重定向回任务列表页面
    return redirect('task_list')

# 视图函数：更新任务状态（完成/未完成）
def task_update(request, task_id):
    # 获取指定 id 的任务，如果不存在则返回 404 错误
    task = get_object_or_404(Task, id=task_id)
    # 切换任务的完成状态
    task.completed = not task.completed
    task.save()
    return redirect('task_list')

# 视图函数：删除任务
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('task_list')
