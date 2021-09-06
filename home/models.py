from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class PemFile(models.Model):
    name = models.CharField(max_length=25)
    user = models.ForeignKey(User, related_name="pemfile", on_delete=models.CASCADE)
    file_path = models.TextField()
    created_date = models.DateField(auto_now_add=True)


class VirtualMachine(models.Model):
    user = models.ForeignKey(User,related_name="vm", on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    memory = models.IntegerField(default=4, help_text="in GB")
    vcpus = models.IntegerField(default=2)
    storage = models.IntegerField(default=20, help_text="in GB")
    mac_address = models.CharField(max_length=50, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    os = models.CharField(max_length=30)
    vpn_ip = models.GenericIPAddressField(blank=True, null=True)
    virtual_mac = models.CharField(max_length=50, blank=True, null=True)
    pem_file = models.ForeignKey(PemFile, on_delete=models.PROTECT, related_name="vm", null=True, blank=True)

    def __str__(self):
        return self.name


