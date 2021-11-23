import logging
import threading

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from home.extra_functions import create_vm, delete_vm
from .models import VirtualMachine

logger = logging.getLogger('home')


@receiver(post_save, sender=VirtualMachine)
def create(sender, instance, created, **kwargs):
    if created:
        logger.info(f"{instance.code} signal functioning adipoli 😀 ")
        threading.Thread(target=create_vm, args=(instance,)).start()


@receiver(pre_delete, sender=VirtualMachine)
def delete(sender, instance, using, **kwargs):
    logger.info(f"{instance.code} signal functioning adipoli 😀 ")
    logger.info(f"{instance.code} deleting vm  😔 ")
    threading.Thread(target=delete_vm, args=(instance,)).start()
