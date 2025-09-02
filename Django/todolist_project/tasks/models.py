# tasks/models.py
from django.db import models
from django.utils import timezone

class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name="任务标题")
    completed = models.BooleanField(default=False, verbose_name="是否完成")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    def __str__(self):
        return self.title

    # Meta 类用于配置模型的行为
    class Meta:
        # 默认排序规则：未完成的在前，然后按创建时间倒序排列
        ordering = ['completed', '-created_at']
