from django.db import models
from django.contrib.auth.models import User

available_os = (('ubuntu_20.04', "ubuntu_20.04",), ("centos_8", "centos_8"))


class VmPlan(models.Model):
    name = models.CharField(max_length=20)
    memory = models.PositiveIntegerField(default=1, help_text="in GB", )
    vcpus = models.PositiveIntegerField(default=1)
    storage = models.PositiveIntegerField(default=10, help_text="in GB")
    os = models.CharField(max_length=20, choices=available_os)
    amount = models.FloatField(help_text='per month')
    image = models.ImageField(upload_to="pic", blank=True, null=True)
    coupon_discount = models.FloatField(help_text='discount', default=0)
    student_discount = models.FloatField(help_text='discount', default=0)

    def __str__(self):
        return self.name


class MarketingMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='marketing')
    coupon = models.CharField(max_length=20, unique=True)
    credits = models.FloatField(default=0)
    total_credits = models.FloatField(default=0)
    total_clients = models.IntegerField(default=0)
    total_active_clients = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=15)
    upi_id = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


class Transaction(models.Model):
    user = models.ForeignKey(User, related_name="request", on_delete=models.CASCADE)
    vm = models.ForeignKey("home.VirtualMachine", related_name="transaction",
                           on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=25, blank=True, null=True)
    plan = models.ForeignKey(VmPlan, related_name='request', on_delete=models.PROTECT, blank=True, null=True)
    month = models.PositiveIntegerField(default=1)
    amount = models.FloatField(default=0)
    transaction_id = models.CharField(default='', max_length=25)
    payment_id = models.CharField(max_length=20, default="")
    payment_status = models.CharField(max_length=20, default="failed")
    date = models.DateField(auto_now_add=True)
    pem_file = models.ForeignKey('home.PemFile', on_delete=models.PROTECT,
                                 related_name="request", null=True, blank=True)
    coupon = models.CharField(max_length=25, blank=True, null=True)
    payment_link = models.CharField(max_length=40, default='')
    amount_only = models.BooleanField(default=0)
    invited_by = models.ForeignKey(MarketingMember, on_delete=models.SET_NULL, blank=True, null=True)
    vm_created = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} "
