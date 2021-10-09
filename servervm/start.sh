cd /home/ubuntu/servervm
source venv/bin/activate
python manage.py runserver &

# celery run tasks from admin
echo "starting beat "
celery -A servervm beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
# worker
echo "starting celery worker"
celery -A servervm worker -l INFO
