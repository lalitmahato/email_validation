from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, chord, group
# from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.enable_utc = False

app.conf.update(timezone='Asia/Kathmandu')

app.autodiscover_tasks()


@app.task
def aggregate_results(results):
    return {"results": results}

@app.task
def get_smtp_records(email):
    from email_service.utils import get_smtp_records
    records = get_smtp_records(email)
    return records
