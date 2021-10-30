from rest_framework import serializers

from .models import VirtualMachine,PemFile,Tokens,VmPlan,VmRequest


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
                  "os", "vpn_ip", "virtual_mac", 'pem_file', 'plan']
        extra_kwargs = {
            'user': {'read_only': True},
            'memory': {'read_only': True},
            'storage': {'read_only': True},
            'vcpus': {'read_only': True},
            'os': {'read_only': True},
            'plan': {'required': True},
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
           'name', 'memory', 'storage', 'amount', 'os', 'vcpus'
        ]


class VmRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmRequest
        fields = ['name', 'pem_file', 'plan', 'month', 'payment_status', 'date', 'payment_id', 'payment_link']
