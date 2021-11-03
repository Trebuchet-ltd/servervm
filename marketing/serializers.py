from rest_framework import serializers

from .models import VmPlan, Transaction, MarketingMember


class GetVmPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmPlan
        fields = [
            'id', 'name', 'memory', 'storage', 'amount', 'os', 'vcpus', 'image', 'student_discount'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'name',"amount",'vm', 'pem_file', 'plan', 'month', 'payment_status', 'date',
                  'payment_id', 'payment_link', 'coupon',]
        extra_kwargs = {
            'payment_status': {'read_only': True},
            'date': {'read_only': True},
            'payment_id': {'read_only': True},
            'payment_link': {'read_only': True},
        }


class MarketingMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingMember

        fields = ['id', "user", "coupon", "credits", "total_credits",
                  "total_clients", "total_active_clients", "phone_number", "upi_id"
                  ]
        extra_kwargs = {
            'user': {'read_only': True},
            'credits': {'read_only': True},
            'total_credits': {'read_only': True},
            'total_clients': {'read_only': True},
            'total_active_clients': {'read_only': True},
        }
