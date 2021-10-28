from django.db import models
from django.contrib.auth.models import User
# Create your models here.
import string
import random
from django.core.validators import MaxValueValidator, MinValueValidator
import os

available_os = (('ubuntu_20.04',"ubuntu_20.04",), ("centos_8", "centos_8"))

def create_new_pem_name():
    not_unique = True
    unique_code = code_generator()
    while not_unique:
        unique_code = code_generator()
        if not PemFile.objects.filter(code=unique_code):
            not_unique = False
    return str(unique_code)


class PemFile(models.Model):
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=15, default=create_new_pem_name, blank=True, null=True)
    user = models.ForeignKey(User, related_name="pemfile", on_delete=models.CASCADE)
    file_path = models.TextField(blank=True,null=True)
    created_date = models.DateField(auto_now_add=True)
    downloaded = models.BooleanField(default=0)

    def __str__(self):
        return f"{self.user} {self.name}"


def code_generator(size=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_new_code():
    not_unique = True
    unique_code = code_generator()
    while not_unique:
        unique_code = code_generator()
        if not VirtualMachine.objects.filter(code=unique_code):
            not_unique = False
    return str(unique_code)


class VirtualMachine(models.Model):

    user = models.ForeignKey(User, related_name="vm", on_delete=models.CASCADE)
    code = models.CharField(max_length=50, default=create_new_code, blank=True, null=True)
    name = models.CharField(max_length=25)
    active = models.BooleanField(default=0)
    memory = models.PositiveIntegerField(default=4, help_text="in GB",
                                         validators=[MinValueValidator(1), MaxValueValidator(16)])
    vcpus = models.PositiveIntegerField(default=2, validators=[MinValueValidator(1), MaxValueValidator(20)])
    storage = models.PositiveIntegerField(default=20, help_text="in GB",
                                          validators=[MinValueValidator(5),])

    mac_address = models.CharField(max_length=50, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    os = models.CharField(max_length=20, choices=available_os)
    vpn_ip = models.GenericIPAddressField(blank=True, null=True)
    virtual_mac = models.CharField(max_length=50, blank=True, null=True)
    pem_file = models.ForeignKey(PemFile, on_delete=models.PROTECT, related_name="vm", null=True, blank=True)
    maintenance = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def start(self):
        os.system(f"virsh start {self.code}")

    def shutdown(self):
        os.system(f"virsh shutdown {self.code}")

    def restart(self):
        os.system(f"virsh start {self.code}")


class SystemDetails(models.Model):
    time = models.TimeField(auto_now_add=True)
    ram_usage = models.FloatField()
    cpu_usage = models.FloatField()
    err_in = models.FloatField(help_text="total number of errors while receiving")
    err_out = models.FloatField(help_text="total number of errors while sending")
    packets_sent = models.FloatField(help_text="number of packets sent")
    packets_recv = models.FloatField(help_text=" number of packets received")
    bytes_sent = models.FloatField(help_text="number of bytes sent")
    bytes_recv = models.FloatField(help_text="number of bytes received")
    dropin = models.FloatField(help_text="total number of incoming packets which were dropped")
    dropout = models.FloatField(help_text="total number of outgoing packets which were dropped")


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_new_id():
    not_unique = True
    unique_id = id_generator()
    while not_unique:
        unique_id = id_generator()
        if not Tokens.objects.filter(private_token=unique_id):
            not_unique = False
    return str(unique_id)


class Tokens(models.Model):
    user = models.OneToOneField(User, related_name='tokens', on_delete=models.CASCADE)
    private_token = models.CharField(max_length=10, unique=True, default=create_new_id)
    invited = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    reviews = models.IntegerField(default=0)
    invite_token = models.CharField(max_length=10, blank=True, null=True)
    first_purchase_done = models.BooleanField(default=False)
    total_points_yet = models.IntegerField(default=0)
    amount_saved = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} "


class VmPlan(models.Model):
    name=models.CharField(max_length=20)
    memory = models.PositiveIntegerField(default=1, help_text="in GB",)
    vcpus = models.PositiveIntegerField(default=1)
    storage = models.PositiveIntegerField(default=10, help_text="in GB")
    os = models.CharField(max_length=20, choices=available_os)
    amount = models.FloatField(help_text='per month')

    def __str__(self):
        return f"{self.os} / {self.memory} gb ram / {self.vcpus} vcpu / " \
               f"{self.storage} gb storage / {self.amount} per month "
