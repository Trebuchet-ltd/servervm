from django.shortcuts import render
from .serializers import VirtualMachineSerializer
from .models import VirtualMachine
from django.contrib.auth.models import User
from rest_framework import viewsets, status, filters
# from rest_framework import permissions
# from rest_framework.decorators import action
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# import sys
from .extra_functions import *
# Create your views here.
import threading


class VmViewSet(viewsets.ModelViewSet):
    serializer_class = VirtualMachineSerializer
    queryset = VirtualMachine.objects.all()
    http_method_names = ['get', 'post', 'patch']

    def perform_create(self, serializer):
        ram = self.request.data["memory"]
        instance = serializer.save(user=self.request.user)
        threading.Thread(target=create_vm, args=(instance, ram)).start()

