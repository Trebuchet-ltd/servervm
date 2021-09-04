from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class VirtualMachine(models.Model):
    user = models.ForeignKey(User,related_name="vm", on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    memory = models.IntegerField(default=4, help_text="in GB")
    storage = models.IntegerField(default=20, help_text="in GB")
    mac_address = models.CharField(max_length=50, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    os = models.CharField(max_length=30)

    def __str__(self):
        return self.name
