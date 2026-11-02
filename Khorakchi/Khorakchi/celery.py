import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Khorakchi.settings")
app = Celery('Khorakchi')
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
