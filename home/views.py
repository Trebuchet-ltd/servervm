from django.shortcuts import render
from .serializers import VirtualMachineSerializer
from .models import VirtualMachine
from django.contrib.auth.models import User
from rest_framework import viewsets, status, filters
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys
import os
import libvirt
import re
import subprocess
import pexpect

# Create your views here.


class VmViewSet(viewsets.ModelViewSet):
    serializer_class = VirtualMachineSerializer
    queryset = VirtualMachine.objects.all()
    http_method_names = ['get', 'post', 'patch']

    def perform_create(self, serializer):
        name = self.request.name
        command = f"virt-clone --original ubuntu2004 --name {name} --file /var/kvm/images/{name}.img"
        os.system(command)
        ram = self.request.memory
        conn = libvirt.open("qemu:///system")
        dom = conn.lookupByName(name)
        dom.setMaxMemory(int(ram) * 1024 * 1024)
        dom.setMemory(int(ram) * 1024 * 1024)
        conn.close()
        mac_address = re.search(r"<mac address='([A-Za-z0-9:]+)'", dom.XMLDesc(0)).groups()
        serializer.save(user= self.request.user, mac_address=mac_address)

