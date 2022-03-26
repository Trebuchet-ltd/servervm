from django.contrib import admin
from .extra_functions import update_vm
from . import models
import threading


@admin.register(models.VirtualMachine)
class VmAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", 'msv', 'active', 'vpn_ip',
                    'plan')

    readonly_fields = ["vpn_ip", "code", 'active', 'ip_address', 'mac_address', 'virtual_mac']
    list_display_links = ['id', 'plan']
    list_filter = ('active', "plan",)
    actions = ['start', 'stop', 'restart', 'update', 'update_without_storage']
    search_fields = ['code', 'name']
    autocomplete_fields = ['user']

    @staticmethod
    def msv(request):
        return f"{request.memory},{request.storage},{request.vcpus}"

    @staticmethod
    def update(self, _, queryset):
        for i in queryset:
            threading.Thread(target=update_vm, args=(i,)).start()

    @staticmethod
    def update_without_storage(self, _, queryset):
        for i in queryset:
            threading.Thread(target=update_vm, args=(i, 0, i.storage)).start()

    @staticmethod
    def start(self, _, queryset):
        for i in queryset:
            i.start()

    @staticmethod
    def stop(self, _, queryset):
        for i in queryset:
            i.stop()

    @staticmethod
    def restart(self, _, queryset):
        for i in queryset:
            i.restart()


@admin.register(models.PemFile)
class PemAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SystemDetails)
class System(admin.ModelAdmin):
    pass
