
from django.http import FileResponse
from rest_framework.decorators import action

from .serializers import VirtualMachineSerializer,PemFileSerializer
from .models import VirtualMachine,PemFile
from django.contrib.auth.models import User
from rest_framework import viewsets, status, filters
# from rest_framework import permissions
# from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
# import sys
from .extra_functions import *
# Create your views here.
import threading
import time
from Crypto.PublicKey import RSA
from os import chmod


class VmViewSet(viewsets.ModelViewSet):
    serializer_class = VirtualMachineSerializer
    queryset = VirtualMachine.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        threading.Thread(target=create_vm, args=(instance,)).start()

    def perform_destroy(self, instance):
        threading.Thread(target=delete_vm, args=(instance,)).start()

    def perform_update(self, serializer):
        print(serializer.validated_data)
        instance = serializer.save(user=self.request.user)
        # print(f"{instance}")
        # threading.Thread(target=update_vm, args=(instance,)).start()

    @action(methods=['post'], detail=False)
    def update_ip(self, request):
        mac_address = request.data["mac_address"]
        vm = VirtualMachine.objects.get(mac_address=mac_address)
        vm.ip_address = request.data["ip_address"]
        vm.save()
        os.system(f"ssh-keygen -q -t rsa -N '' -f /home/ubuntu/{vm.name} <<y")
        time.sleep(10)
        os.system(f"sshpass -p '12345678' ssh-copy-id -f -i {vm.pem_file.file_path}.pub -o StrictHostKeyChecking=no test@{vm.ip_address} ")
        os.system(f"sshpass -p '12345678' ssh test@{vm.ip_address} bash /var/local/remove_password.sh > err.html ")
        return Response(status=201)

    @action(methods=['post'], detail=False)
    def set_vpn_ip(self, request):
        mac_address = request.POST["mac_address"]
        vm = VirtualMachine.objects.get(mac_address=mac_address)
        vm.vpn_ip = request.POST["vpn_ip"]
        vm.virtual_mac = request.POST["virtual_mac"]
        vm.save()
        return Response(status=201)


class PemFileViewSet(viewsets.ModelViewSet):

    """
    Api end point to generate pem file
    """

    serializer_class = PemFileSerializer
    queryset = PemFile.objects.all()
    http_method_names = ["get", "post", "delete" ]

    def perform_create(self, serializer):
        name = self.request.data['name']
        os.makedirs(f"/home/ubuntu/servervm/media/{self.request.user}", exist_ok=True)

        os.system(f"ssh-keygen -q -t rsa -N '' -f /home/ubuntu/servervm/media/{self.request.user}/{name} <<y")
        serializer.save(user=self.request.user,
                        file_path=f"/home/ubuntu/servervm/media/{self.request.user}/{name}")

    @action(methods=["get"], detail=True)
    def download_file(self, request, pk):
        pem_file = PemFile.objects.get(pk=pk)
        pem = open(pem_file.file_path, 'rb')
        response = FileResponse(pem)
        os.remove(pem_file.file_path)
        return response

