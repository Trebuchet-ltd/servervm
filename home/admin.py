from django.contrib import admin
from .models import VirtualMachine
# Register your models here.


@admin.register(VirtualMachine)
class VmAdmin(admin.ModelAdmin):
    pass
