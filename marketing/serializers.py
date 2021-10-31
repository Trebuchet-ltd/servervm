from rest_framework import serializers

from .models import VmPlan, VmRequest, MarketingMember


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
        extra_kwargs = {
            'payment_status': {'read_only': True},
            'date': {'read_only': True},
            'payment_id': {'read_only': True},
            'payment_link': {'read_only': True},
        }


class MarketingMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingMember

        fields = ['id', "user", "coupon", "credits", "total_credits", "total_clients", "total_active_clients"]
        extra_kwargs = {
            'user': {'read_only': True},
            'coupon': {'read_only': True},
            'credits': {'read_only': True},
            'total_credits': {'read_only': True},
            'total_clients': {'read_only': True},
            'total_active_clients': {'read_only': True},

        }
