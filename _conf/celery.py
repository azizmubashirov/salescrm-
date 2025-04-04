from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_conf.settings')

app = Celery('_conf')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'myproject.settings':
    import multiprocessing
    multiprocessing.set_start_method('spawn')
    
app.conf.timezone = 'Asia/Tashkent'
app.conf.enable_utc = False
