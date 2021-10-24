import os

from celery import Celery
from celery.signals import worker_ready

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servervm.settings')

app = Celery('servervm',
             include=['home.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'home.tasks.add',
        'schedule': 30.0,
    },
}
app.conf.beat_schedule = {
    'vm monitoring in every 5 minutes': {
        'task': 'home.tasks.monitor_vm',
        'schedule': 60 * 3,
    },
}


@worker_ready.connect
def at_start(sender, **k):
    with sender.app.connection() as conn:
        sender.app.send_task('home.tasks.monitor_vm', )


app.conf.timezone = 'Asia/Kolkata'
