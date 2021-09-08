import libvirt
import re
import pexpect
import os
import subprocess
import time
from .models import Storage


def set_storage(instance):
    """
    --->  This function first create a img file with new file size
    --->  Then change the permission to qmeu:kvm
    --->  then expand the vm disk with new image
    --->  then remove old img and rename new image to old name

    :param instance: the instance of model VirtualMachine
    :return:
    """

    storage = instance.storage
    os.system(
        f"sudo qemu-img create -f qcow2 -o preallocation=metadata /var/kvm/images/{instance.name}-new.qcow2 {storage}G")
    os.system(f"sudo chown libvirt-qemu:kvm /var/kvm/images/{instance.name}-new.qcow2")
    os.system(
        f"sudo virt-resize --expand /dev/vda3 /var/kvm/images/{instance.name}.qcow2 /var/kvm/images/{instance.name}-new.qcow2")
    os.system(f"sudo rm /var/kvm/images/{instance.name}.qcow2")
    os.system(f"sudo mv /var/kvm/images/{instance.name}-new.qcow2 /var/kvm/images/{instance.name}.qcow2")


def set_memory(instance, dom,vcpu=True):
    """
    --->  This function first change the max memory
    --->  Then change the permission to qmeu:kvm
    --->  then expand the vm disk with new image
    --->  then remove old img and rename new image to old name

    :param instance: the instance of model VirtualMachine
    :param dom:
    :param vcpu:
    :return:
    """

    ram = instance.memory
    dom.setMaxMemory(int(ram) * 1024 * 1024)
    os.system(f"virsh setvcpus {instance.name} {instance.vcpus} --config --maximum")
    os.system(f"virsh setvcpus {instance.name} {instance.vcpus} --config ")
    os.system(f"virsh start {instance.name}")
    os.system(f"virsh setvcpus --count {instance.vcpus} {instance.name} ")
    time.sleep(5)
    dom.setMemory(int(ram) * 1024 * 1024)


def create_vm(instance):
    command = f"virt-clone --original ubuntu2004 --name {instance.name} --file /var/kvm/images/{instance.name}.qcow2"
    os.system(command)
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(instance.name)

    set_storage(instance)
    set_memory(instance, dom)
    conn.close()
    mac_address = re.search(r"<mac address='([A-Za-z0-9:]+)'", dom.XMLDesc(0)).groups()[0]
    instance.mac_address = mac_address
    Storage.objects.create(vm=instance, size=20, file_path=f"/var/kvm/images/{instance.name}.img")
    instance.save()


def delete_vm(instance):
    os.system(f"rm /home/ubuntu/{instance.name}")
    os.system(f"rm /home/ubuntu/{instance.name}.pub")

    conn = libvirt.open("qemu:///system")
    try:
        dom = conn.lookupByName(instance.name)
        if dom.isActive():
            os.system(f"virsh shutdown {instance.name}")
            time.sleep(10)
        os.system(f"virsh undefine {instance.name} --remove-all-storage")
    except Exception as e:
        print(e)
    instance.delete()


def update_vm(instance):
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(instance.name)

    os.system(f"virsh shutdown {instance.name}")
    time.sleep(20)
    print("shut down completed")
    set_storage(instance)
    set_memory(instance, dom)
    conn.close()

