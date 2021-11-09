
from django.contrib import admin
from . import models


@admin.register(models.VmPlan)
class System(admin.ModelAdmin):
    list_display = ('name', 'vcpus', 'memory', 'storage')
    ordering = ['vcpus']


@admin.register(models.MarketingMember)
class MarketingMembers(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'credits', 'total_active_clients')


@admin.register(models.Transaction)
class Transaction(admin.ModelAdmin):
    pass

