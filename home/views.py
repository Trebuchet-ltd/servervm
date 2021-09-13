
from django.http import FileResponse
from rest_framework.decorators import action

from .serializers import VirtualMachineSerializer, PemFileSerializer
from .models import VirtualMachine, PemFile
from rest_framework import viewsets
from rest_framework.response import Response
from .extra_functions import *
import threading
import time
import servervm.settings as settings


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
        threading.Thread(target=update_vm, args=(instance,)).start()

    @action(methods=['post'], detail=False)
    def update_ip(self, request):
        print(request.data)
        mac_address = request.data["mac_address"]
        vm = VirtualMachine.objects.get(mac_address=mac_address)
        if not vm.ip_address:
            vm.ip_address = request.data["ip_address"]
            vm.save()
            os.system(f"ssh-keygen -q -t rsa -N '' -f /home/ubuntu/{vm.name} <<y")
            time.sleep(10)
            os.system(f"sshpass -p '{settings.vm_template_password}' ssh-copy-id -f -i {vm.pem_file.file_path}.pub -o StrictHostKeyChecking=no user@{vm.ip_address} ")
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
    http_method_names = ["get", "post", "delete" ]

    def perform_create(self, serializer):
        name = self.request.data['name']
        os.makedirs(f"/home/ubuntu/servervm/media/{self.request.user}", exist_ok=True)
        instance = serializer.save(user=self.request.user,
                                   file_path=f"/home/ubuntu/servervm/media/{self.request.user}/{name}")
        os.system(f"ssh-keygen -q -t rsa -N '' -f /home/ubuntu/servervm/media/{self.request.user.id}/{instance.id} <<y")

    @action(methods=["get"], detail=True)
    def download_file(self, request, pk):
        pem_file = PemFile.objects.get(pk=pk)
        pem = open(pem_file.file_path, 'rb')
        response = FileResponse(pem, filename=pem_file.name)
        os.remove(pem_file.file_path)
        return response

