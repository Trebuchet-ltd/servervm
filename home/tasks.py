from servervm.celery import *
from home.models import SystemDetails
import psutil
import logging

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls test('hello') every 10 seconds.
#     sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
#
#     # Calls test('world') every 30 seconds
#     sender.add_periodic_task(30.0, test.s('world'), expires=10)


#
# @app.task
# def test(arg):
#     print(arg)
#
# @app.task
# def add(x, y):
#     z = x + y
#     print(z)

@app.task
def add():
    logging.info("system checking started")
    logging.info("checking cpu usage")
    cpu = psutil.cpu_percent()
    logging.info(f"cpu usage is {cpu}%")
    logging.info("checking ram usage")
    ram = psutil.virtual_memory().percent
    logging.info(f"ram usage is {ram}%")
    SystemDetails.objects.create(cpu_usage=cpu, ram_usage=ram)
    logging.info("checking completed")
    return 0

