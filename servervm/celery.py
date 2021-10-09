import os
from celery.schedules import crontab
# from celery.decorators import periodic_task
import logging
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servervm.settings')


app = Celery('servervm',
             include=['home.tasks'])

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configpiuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
print(app.tasks)
logging.info(f"app {app.tasks}")
# app.conf.beat_schedule = {
#     # Executes every Monday morning at 7:30 a.m.
#     'every-1-minutes': {
#         'task': 'tasks.add',
#         'schedule': crontab(minute='*/1'),
#     },
# }
app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'home.tasks.add',
        'schedule': 30.0,
    },
}

app.conf.timezone = 'Asia/Kolkata'
# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
# celeryd --loglevel=INFO --settings=celeryconfig

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')