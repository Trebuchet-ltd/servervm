from rest_framework import serializers

from .models import VirtualMachine


class VirtualMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualMachine
        fields = ["id", "name", "memory", "storage", "ip_address", "mac_address", "os", "vpn_ip", "virtual_mac"]

