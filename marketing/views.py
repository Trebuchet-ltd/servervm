import logging
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

import servervm.settings as settings
from authentication.permissions import IsOwner
from home.extra_functions import handle_payment, verify_signature, get_payment_link
from home.models import VirtualMachine, PemFile
from .models import VmPlan, Transaction, MarketingMember
from .serializers import GetVmPlanSerializer, TransactionSerializer, MarketingMemberSerializer

logger = logging.getLogger("marketing")


class VmPlanViewSet(viewsets.ModelViewSet):
    serializer_class = GetVmPlanSerializer
    queryset = VmPlan.objects.all()
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]


class TransactionAPiViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        try:
            return Transaction.objects.filter(user=self.request.user)
        except Transaction.DoesNotExist:
            return Transaction.objects.none()

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        plan = request.data.get('plan')
        vm = request.data.get('vm')
        month = request.data.get("month")
        amount = request.data.get("amount")
        coupon = request.data.get("coupon")
        pem_file = request.data.get("pem_file")
        serializer = self.get_serializer(data=request.data)
        if not (name or pem_file or plan or month or vm) and amount:
            logger.info(f"{request.user} requested to pay {amount} rupees (amount only) ")
            serializer.is_valid(raise_exception=True)
            obj = serializer.save(user=request.user, amount_only=True)
            get_payment_link(self.request.user, obj, amount=amount)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.info(f"{request.user} requested for payment")


class MarketingMemberViewSet(viewsets.ModelViewSet):
    serializer_class = MarketingMemberSerializer
    queryset = MarketingMember.objects.all()
    permission_classes = [IsOwner, permissions.IsAuthenticated]
    http_method_names = ['get', "post"]

    def create(self, request, *args, **kwargs):
        try:
            MarketingMember.objects.get(user=self.request.user)
            return Response({"detail": "user has already created marketing account"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        except MarketingMember.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def payment(request):
    print(request)
    logger.info("Webhook from razorpay called ...")
    if verify_signature(request):
        transaction_id = request.GET["razorpay_payment_link_reference_id"]
        handle_payment(transaction_id)
    else:
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    return HttpResponseRedirect(settings.webhook_redirect_url)


@api_view(["POST"])
def apply_coupon(request):
    coupon = request.data.get("coupon")
    discount = 0
    if coupon:
        try:
            MarketingMember.objects.get(coupon__iexact=coupon)
            logger.info(f"found coupon")
            discount = 50
        except MarketingMember.DoesNotExist:
            return Response({"detail": "invalid coupon"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    logger.info(f"total discount is {discount}")
    return Response({"discount": discount}, status=status.HTTP_200_OK)
