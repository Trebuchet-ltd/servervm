from django.contrib import admin
from .models import VirtualMachine,PemFile
# Register your models here.


@admin.register(VirtualMachine)
class VmAdmin(admin.ModelAdmin):
    pass

@admin.register(PemFile)
class PemAdmin(admin.ModelAdmin):
    pass
