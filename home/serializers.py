from rest_framework import serializers

from .models import VirtualMachine,PemFile


class PemFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PemFile
        fields = ["id", 'name',"user", "created_date"]
        extra_kwargs = {
            'user': {'read_only': True},
        }


class VirtualMachineSerializer(serializers.ModelSerializer):

    class Meta:
        model = VirtualMachine
        fields = ["id", "name", "memory", "storage", 'vcpus', "ip_address", "mac_address",
                  "os", "vpn_ip", "virtual_mac", 'pem_file']
        extra_kwargs = {
            'user': {'read_only': True},
            "ip_address": {'read_only': True},
            "vpn_ip": {'read_only': True},
            "virtual_mac": {'read_only': True},
            "mac_address": {'read_only': True},

        }

