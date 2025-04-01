import os
from celery import Celery

# 设置 Django 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamemall.settings')

# 创建 Celery 实例
app = Celery('gamemall')

# 从 Django 配置加载设置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有应用中的 tasks.py
app.autodiscover_tasks()