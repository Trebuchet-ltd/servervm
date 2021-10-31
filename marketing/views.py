#
# import django_filters
# from django.http import FileResponse
# from rest_framework.decorators import action
import logging

from .serializers import  GetVmPlanSerializer, VmRequestSerializer,MarketingMemberSerializer
from .models import  VmPlan,VmRequest,MarketingMember

from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from home.extra_functions import handle_payment, verify_signature, get_payment_link

import servervm.settings as settings
from rest_framework import status
from authentication.permissions import IsOwner
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect

logger = logging.getLogger("marketing")


class VmPlanViewSet(viewsets.ModelViewSet):
    serializer_class = GetVmPlanSerializer
    queryset = VmPlan.objects.all()
    http_method_names = ['get']


class VmRequestAPiViewSet(viewsets.ModelViewSet):
    serializer_class = VmRequestSerializer
    queryset = VmRequest.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    http_method_names = ['get', 'post', 'patch']

    def perform_create(self, serializer):
        obj = serializer.save(user=self.request.user)
        get_payment_link(self.request.user, obj)


class MarketingMemberViewSet(viewsets.ModelViewSet):
    serializer_class = MarketingMemberSerializer
    queryset = MarketingMember.objects.all()
    permission_classes = [IsOwner]
    http_method_names = ['get']

    def get_queryset(self):
        if self.request.user.marketing.exists():
            return MarketingMember.objects.get(user=self.request.user)
        return MarketingMember.objects.none()


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



