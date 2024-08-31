# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Create a Celery instance
app = Celery('project')

# Load Celery configuration from Django settings, using the CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all registered Django app configs
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
