from django.contrib import admin, messages
from . import models


# Register your models here.


@admin.register(models.VirtualMachine)
class VmAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "code", "name", 'active', "memory", "storage", 'vcpus',
                    "vpn_ip", 'plan', )

    list_filter = ('active', "plan",)
    actions = ['start', 'stop', 'restart']

    def start(self, request, queryset):
        for i in queryset:
            i.start()

    def stop(self, request, queryset):
        for i in queryset:
            i.shutdown()

    def restart(modeladmin, request, queryset):
        for i in queryset:
            i.restart()


@admin.register(models.PemFile)
class PemAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SystemDetails)
class System(admin.ModelAdmin):
    pass
