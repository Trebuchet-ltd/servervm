from django.contrib import admin
from .models import VirtualMachine,PemFile,SystemDetails,VmPlan
# Register your models here.


@admin.register(VirtualMachine)
class VmAdmin(admin.ModelAdmin):
    pass


@admin.register(PemFile)
class PemAdmin(admin.ModelAdmin):
    pass


@admin.register(SystemDetails)
class System(admin.ModelAdmin):
    pass


@admin.register(VmPlan)
class System(admin.ModelAdmin):
    pass
