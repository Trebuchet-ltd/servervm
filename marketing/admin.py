
from django.contrib import admin
from . import models


@admin.register(models.VmPlan)
class System(admin.ModelAdmin):
    pass


@admin.register(models.MarketingMember)
class MarketingMembers(admin.ModelAdmin):
    pass


@admin.register(models.Transaction)
class Transaction(admin.ModelAdmin):
    pass

