
# import django_filters
# from django.http import FileResponse
# from rest_framework.decorators import action
import logging
from .serializers import GetVmPlanSerializer, TransactionSerializer, MarketingMemberSerializer
from .models import VmPlan, Transaction, MarketingMember
from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from home.extra_functions import handle_payment, verify_signature, get_payment_link

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


class TransactionAPiViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        name = request.data['name']
        plan = request.data['plan']
        vm = request.data['vm']
        pem_file = request.data["pem_file"]
        logger.info(f"{request.user} requested for payment")
        if vm:
            try:
                vm_obj = VirtualMachine.objects.get(pk=vm)
                logger.info(f"{request.user} seleceted {vm_obj}")

                if vm_obj.user != request.user:
                    logger.info("user is not authenticated for this vm")
                    return Response({"detail": "You are not authenticated to this virtual machine "},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)

            except VirtualMachine.DoesNotExist:
                logger.info("invalid vm id")
                return Response({"detail": "Virtual machine does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not plan:
            logger.info("plan is not selected")
            return  Response({"detail": "plan is required"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            logger.info("user not provided vm id ")
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
                        print(f"{request.user } does not match with {pem.user}")
                        return Response({"detail": "You are not authenticated to this key file "},
                                        status=status.HTTP_406_NOT_ACCEPTABLE)
                except PemFile.DoesNotExist:
                    print(f"pem file is not valid one")
                    return Response({"detail": "key file does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(user=request.user)
        logger.debug(obj)
        if vm and not plan:
            obj.plan = VirtualMachine.objects.get(pk=vm).plan
            logger.warning(obj)
            obj.save()
        get_payment_link(self.request.user,  obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarketingMemberViewSet(viewsets.ModelViewSet):
    serializer_class = MarketingMemberSerializer
    queryset = MarketingMember.objects.all()
    permission_classes = [IsOwner,permissions.IsAuthenticated]
    http_method_names = ['get', "post"]

    def create(self, request, *args, **kwargs):
        try:
            MarketingMember.objects.get(user=self.request.user)
            return Response({"detail": "user has already created marketing account"},status=status.HTTP_406_NOT_ACCEPTABLE)
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
