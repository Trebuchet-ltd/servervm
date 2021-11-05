
from servervm.celery import *
from home.models import SystemDetails
import psutil
from home.models import VirtualMachine
import libvirt
from django.core.mail import send_mail

from celery.utils.log import get_task_logger

logger = get_task_logger("tasks")


@app.task
def server_monitoring():
    logger.info("system checking started")
    logger.info("checking cpu usage")
    cpu = psutil.cpu_percent()
    logger.info(f"cpu usage is {cpu}%")
    logger.info("checking ram usage")
    ram = psutil.virtual_memory().percent
    logger.info(f"ram usage is {ram}%")
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

    logger.info("checking completed")


@app.task
def monitor_vm():
    vms = VirtualMachine.objects.all()
    conn = libvirt.open("qemu:///system")
    for vm in vms:

        try:
            dom = conn.lookupByName(vm.code)
            logger.info(f"vm {vm.code}/{vm.name} 's active status in database {vm.active} actually {dom.isActive()}")
            if vm.active and not dom.isActive():
                logger.info(f"vm {vm.code}/{vm.name} is not on but it is active according to database ")
                logger.info(f"vm {vm.code}/{vm.name} is starting  ")
                os.system(f"virsh start {vm.code}")
                logger.info(f"vm {vm.code}/{vm.name} is started  ")
        except Exception as e:
            logger.warning(e)


# @app.task
# def reduce_credits():
#     vms = VirtualMachine.objects.filter(staff_status=False)
#     conn = libvirt.open("qemu:///system")
#     for vm in vms:
#         try:
#             dom = conn.lookupByName(vm.code)
#             logger.info(f"vm {vm.code}/{vm.name} 's active status in database {vm.active} actually {dom.isActive()}")
#             if vm.active and not dom.isActive():
#                 logger.info(f"vm {vm.code}/{vm.name} is not on but it is active according to database ")
#                 logger.info(f"vm {vm.code}/{vm.name} is starting  ")
#                 os.system(f"virsh start {vm.code}")
#                 logger.info(f"vm {vm.code}/{vm.name} is started  ")
#         except Exception as e:
#             logger.warning(e)
