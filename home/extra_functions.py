import libvirt
import re
import pexpect
import os
import subprocess
import time


def create_vm(instance):
    command = f"virt-clone --original ubuntu2004 --name {instance.name} --file /var/kvm/images/{instance.name}.img"
    os.system(command)
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(instance.name)
    ram = instance.memory
    dom.setMaxMemory(int(ram) * 1024 * 1024)
    os.system(f"virsh setvcpus {instance.name} {instance.vcpus} --config --maximum")
    os.system(f"virsh setvcpus {instance.name} {instance.vcpus} --config ")
    os.system(f"virsh start {instance.name}")
    time.sleep(5)

    dom.setMemory(int(ram) * 1024 * 1024)
    os.system(f"virsh setvcpus --count {instance.vcpus} {instance.name} ")

    conn.close()
    mac_address = re.search(r"<mac address='([A-Za-z0-9:]+)'", dom.XMLDesc(0)).groups()[0]
    instance.mac_address = mac_address
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
    dom.shutdown()
    time.sleep(10)
    ram = instance.memory
    dom.setMaxMemory(int(ram) * 1024 * 1024)
    os.system(f"virsh setvcpus {instance.name} {instance.vcpus} --config --maximum")
    os.system(f"virsh setvcpus {instance.name} {instance.vcpus} --config ")
    os.system(f"virsh start {instance.name}")
    time.sleep(5)

    dom.setMemory(int(ram) * 1024 * 1024)
    os.system(f"virsh setvcpus --count {instance.vcpus} {instance.name} ")

    conn.close()