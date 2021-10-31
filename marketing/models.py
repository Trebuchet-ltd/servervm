from django.db import models
from django.contrib.auth.models import User


available_os = (('ubuntu_20.04', "ubuntu_20.04",), ("centos_8", "centos_8"))


class VmPlan(models.Model):
    name = models.CharField(max_length=20)
    memory = models.PositiveIntegerField(default=1, help_text="in GB",)
    vcpus = models.PositiveIntegerField(default=1)
    storage = models.PositiveIntegerField(default=10, help_text="in GB")
    os = models.CharField(max_length=20, choices=available_os)
    amount = models.FloatField(help_text='per month')

    def __str__(self):
        return f"{self.os} / {self.memory} gb ram / {self.vcpus} vcpu / " \
               f"{self.storage} gb storage / {self.amount} per month "


class MarketingMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='marketing', blank=True, null=True)
    coupon = models.CharField(max_length=20)
    credits = models.FloatField(default=0)
    total_credits = models.FloatField(default=0)
    total_clients = models.IntegerField(default=0)
    total_active_clients = models.IntegerField(default=0)


class VmRequest(models.Model):
    user = models.ForeignKey(User, related_name="request", on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    plan = models.ForeignKey(VmPlan,related_name='request',on_delete=models.PROTECT)
    month = models.PositiveIntegerField(default=1)
    transaction_id = models.CharField(default='', max_length=25)
    payment_id = models.CharField(max_length=20, default="")
    payment_status = models.CharField(max_length=20, default="failed")
    date = models.DateField(auto_now=True)
    pem_file = models.ForeignKey('home.PemFile', on_delete=models.PROTECT, related_name="request", null=True, blank=True)
    payment_link = models.CharField(max_length=40, default='')

