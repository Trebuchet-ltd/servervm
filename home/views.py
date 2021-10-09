import os

from django.http import FileResponse
from rest_framework.decorators import action

from .serializers import VirtualMachineSerializer, PemFileSerializer
from .models import VirtualMachine, PemFile
from rest_framework import viewsets, status
from rest_framework.response import Response
from .extra_functions import *
import threading
import time
import servervm.settings as settings
from .tasks import add


class VmViewSet(viewsets.ModelViewSet):
    serializer_class = VirtualMachineSerializer
    queryset = VirtualMachine.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        threading.Thread(target=create_vm, args=(instance,)).start()

    def perform_destroy(self, instance):
        threading.Thread(target=delete_vm, args=(instance,)).start()

    def update(self, request, *args, **kwargs):
        current_data = VirtualMachine.objects.get(id=self.request.data["id"])
        memory = current_data.memory
        storage = current_data.storage
        new_storage = self.request.data["storage"]
        print(f"{memory = }, {new_storage = } {storage = }")
        res = super().update(self.request, *args, **kwargs)
        current_data = VirtualMachine.objects.get(id=self.request.data["id"])
        threading.Thread(target=update_vm, args=(current_data, memory, storage)).start()
        return res

    @action(methods=['post'], detail=True)
    def start(self, request, pk):
        vm = VirtualMachine.objects.get(pk=pk)
        conn = libvirt.open("qemu:///system")
        try:
            dom = conn.lookupByName(vm.code)
            if not dom.isActive():
                dom.create()
            else:
                return Response("vm already active")
        except Exception as e:
            print(e)
        return Response("vm started")

    @action(methods=['post'], detail=True)
    def stop(self, request, pk):
        vm = VirtualMachine.objects.get(pk=pk)
        conn = libvirt.open("qemu:///system")
        try:
            dom = conn.lookupByName(vm.code)
            try:
                dom.shutdown()
            except Exception as e:
                print(e)
                return Response("vm already off")
        except Exception as e:
            print(e)
        return Response("vm shutdown")

    @action(methods=['post'], detail=True)
    def restart(self, request, pk):
        vm = VirtualMachine.objects.get(pk=pk)
        conn = libvirt.open("qemu:///system")
        try:
            dom = conn.lookupByName(vm.code)
            if dom.isActive():
                dom.reboot()
            else:
                return Response("vm already off")
        except Exception as e:
            print(e)
        return Response("vm is rebooting")

    @action(methods=['get'],detail=False)
    def test(self, request):
        add.delay()
        return Response(status=201)

    @action(methods=['post'], detail=False)
    def update_ip(self, request):
        print(request.data)
        mac_address = request.data["mac_address"]
        vm = VirtualMachine.objects.get(mac_address=mac_address)
        if not vm.ip_address:
            vm.ip_address = request.data["ip_address"]
            vm.save()
            os.system(f'ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "{vm.ip_address}"')
            os.system(f"ssh-keygen -q -t rsa -N '' -f /home/ubuntu/{vm.code} <<y")
            time.sleep(10)
            os.system(f"sshpass -p '{settings.vm_template_password}' ssh-copy-id -f -i {vm.pem_file.file_path}.pub -o StrictHostKeyChecking=no user@{vm.ip_address} ")
            print("one")
            os.system(f"sshpass -p '{settings.vm_template_password}' ssh -o StrictHostKeyChecking=no user@{vm.ip_address} bash /var/local/setup.sh > err.html ")
        return Response(status=201)

    @action(methods=['post'], detail=False)
    def set_vpn_ip(self, request):
        mac_address = request.POST["mac_address"]
        vm = VirtualMachine.objects.get(mac_address=mac_address)
        if not vm.vpn_ip:
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
    http_method_names = ["get", "post", "delete"]

    def perform_create(self, serializer):
        name = self.request.data['name']
        os.makedirs(f"/home/ubuntu/servervm/media/{self.request.user}", exist_ok=True)
        instance = serializer.save(user=self.request.user)
        instance.file_path = f"/home/ubuntu/servervm/media/{self.request.user}/{instance.code}"
        instance.save()
        os.system(f"ssh-keygen -q -t rsa -N '' -f /home/ubuntu/servervm/media/{self.request.user}/{instance.code}<<y")

    @action(methods=["get"], detail=True)
    def download_file(self, request, pk):
        pem_file = PemFile.objects.get(pk=pk)
        if not pem_file.downloaded:
            pem = open(pem_file.file_path, 'rb')
            print(pem)
            response = FileResponse(pem, filename=pem_file.name)
            os.remove(pem_file.file_path)
            pem_file.downloaded = 1
            pem_file.save()
            return response
        return Response({"error": "you have already downloaded this file"})

