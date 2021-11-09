import logging
import threading

from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from .serializers import GetVmPlanSerializer, TransactionSerializer, MarketingMemberSerializer
from .models import VmPlan, Transaction, MarketingMember
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from home.extra_functions import handle_payment, verify_signature, get_payment_link, calculate_amount
from rest_framework.views import APIView
import servervm.settings as settings
from rest_framework import status
from authentication.permissions import IsOwner
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect
from home.models import VirtualMachine, PemFile

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

        if vm:
            try:
                vm_obj = VirtualMachine.objects.get(pk=vm)
                logger.info(f"{request.user} selected {vm_obj}")

                if vm_obj.user != request.user:
                    logger.info("user is not authenticated for this vm")
                    return Response({"detail": "You are not authenticated to this virtual machine "},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
            except VirtualMachine.DoesNotExist:
                logger.info("invalid vm id")
                return Response({"detail": "Virtual machine does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not plan:
            logger.info("plan is not selected")
            return Response({"detail": "plan is required"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            logger.info("user not provided vm id ")
            if not name:
                logger.info("name is not provided")
                return Response({"detail": "name is required"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            elif not plan:
                logger.info("plan is not selected")
                return Response({"detail": "plan is required"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            elif not pem_file:
                logger.info("pem file is not provided")
                return Response({"detail": "key file is required"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                try:
                    pem = PemFile.objects.get(pk=pem_file)
                    print(f"found the pem file validating")
                    if pem.user != request.user:
                        print(f"{request.user} does not match with {pem.user}")
                        return Response({"detail": "You are not authenticated to this key file "},
                                        status=status.HTTP_406_NOT_ACCEPTABLE)
                except PemFile.DoesNotExist:
                    print(f"pem file is not valid one")
                    return Response({"detail": "key file does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            logger.info("checking plan")
            if plan:
                try:
                    vm_pln = VmPlan.objects.get(pk=plan)
                    if vm:
                        vm_obj = VirtualMachine.objects.get(pk=vm)
                        if vm_pln.vcpus < vm_obj.vcpus:
                            logger.info("user tried to downgrade the plan")
                            return Response({"detail": "virtual machine plan downgrading is not allowed "},
                                            status=status.HTTP_406_NOT_ACCEPTABLE)

                except VmPlan.DoesNotExist:
                    logger.info("user is not authenticated for this vm")
                    return Response({"detail": "Selected plan does not exist"},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer.is_valid(raise_exception=True)
        obj = serializer.save(user=request.user)
        logger.debug(obj)
        if vm and not plan:
            obj.plan = VirtualMachine.objects.get(pk=vm).plan
            logger.info(obj)
            obj.save()
        get_payment_link(self.request.user, obj)
        if request.user.is_staff:
            vm_id = handle_payment(obj.transaction_id)
            if vm_id != -1:
                return Response({"payment_link": f"{settings.webhook_redirect_url}/{vm_id}"},status=status.HTTP_200_OK)
            return Response({"payment_link": f"{settings.webhook_redirect_url}/"},status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
def apply_coupon( request):
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
