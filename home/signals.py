import threading

from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from .models import VirtualMachine
import logging
from home.extra_functions import create_vm,delete_vm


@receiver(post_save, sender=VirtualMachine)
def create(sender, instance, created, **kwargs):
    if created:
        logging.info(f"{instance.code} signal functioning adipoli 😀 ")
        threading.Thread(target=create_vm, args=(instance,)).start()


@receiver(pre_delete, sender=VirtualMachine)
def delete(sender, instance, using, **kwargs):
    logging.info(f"{instance.code} signal functioning adipoli 😀 ")
    threading.Thread(target=delete_vm, args=(instance,)).start()
