"""
Celery configuration for healthcare project.

This module initializes the Celery application and configures it
to work with Django settings.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery application
app = Celery('healthcare')

# Load configuration from Django settings, using a CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all registered Django apps
# This will look for tasks.py in each app
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery is working correctly."""
    print(f'Request: {self.request!r}')
