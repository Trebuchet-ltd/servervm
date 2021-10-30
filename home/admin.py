from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.VirtualMachine)
class VmAdmin(admin.ModelAdmin):
    pass


@admin.register(models.PemFile)
class PemAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SystemDetails)
class System(admin.ModelAdmin):
    pass


@admin.register(models.VmPlan)
class System(admin.ModelAdmin):
    pass


@admin.register(models.MarketingMember)
class MarketingMembers(admin.ModelAdmin):
    pass


@admin.register(models.VmRequest)
class VmRequest(admin.ModelAdmin):
    pass
