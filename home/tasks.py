from servervm.celery import *
from home.models import SystemDetails
import psutil
import logging


@app.task
def add():
    logging.info("system checking started")
    logging.info("checking cpu usage")
    cpu = psutil.cpu_percent()
    logging.info(f"cpu usage is {cpu}%")
    logging.info("checking ram usage")
    ram = psutil.virtual_memory().percent
    logging.info(f"ram usage is {ram}%")
    net_io = psutil.net_io_counters(pernic=False, nowrap=True)

    SystemDetails.objects.create(
            cpu_usage=cpu,
            ram_usage=ram,
            err_out=net_io.errout,
            err_in=net_io.errin,
            packets_sent=net_io.packets_sent,
            packets_recv=net_io.packets_recv,
            bytes_sent=net_io.bytes_sent,
            bytes_recv=net_io.bytes_recv,
            dropin=net_io.dropin,
            dropout=net_io.dropout,
            )

    logging.info("checking completed")


@app.task
def monitor_vm():
    pass