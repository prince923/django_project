from celery import Celery

import os
# if not os.getenv('DJANGO_SETTINGS_MODULE'):
#     os.environ['DJANGO_SETTINGS_MODULE'] = 'dj_pre_class.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

app = Celery('django_project')  # 创建celery应用

app.config_from_object('celery_tasks.celery_config')  # 导入celery配置

# 导入任务
app.autodiscover_tasks(['celery_tasks.sms', ])