from rest_framework import serializers

from .models import VirtualMachine,PemFile,Tokens,VmPlan


class PemFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PemFile
        fields = ["id", 'name',"user", "created_date", "file_path"]
        extra_kwargs = {
            'user': {'read_only': True},
            "file_path": {'read_only': True},
        }


class VirtualMachineSerializer(serializers.ModelSerializer):

    class Meta:
        model = VirtualMachine
        fields = ["id", "code", "name",'active',"memory", "storage", 'vcpus', "ip_address", "mac_address",
                  "os", "vpn_ip", "virtual_mac", 'pem_file']
        extra_kwargs = {
            'user': {'read_only': True},
            "ip_address": {'read_only': True},
            "vpn_ip": {'read_only': True},
            "virtual_mac": {'read_only': True},
            "mac_address": {'read_only': True},
            "code": {'read_only': True},
            "active": {'read_only': True},
        }


class GetTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tokens
        fields = [
            'user', 'private_token', 'invite_token', 'invited', 'points',

        ]


class GetVmPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmPlan
        fields = [
            'memory', 'storage', 'amount', 'os','vcpus'
        ]
