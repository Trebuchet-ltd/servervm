import libvirt
import re
import os
import subprocess
import time

import math


def set_storage(instance):
    """
    --->  This function first create a img file with new file size
    --->  Then change the permission to qmeu:kvm
    --->  then expand the vm disk with new image
    --->  then remove old img and rename new image to old name

    :param instance: the instance of model VirtualMachine
    :return:
    """

    storage = int(math.fabs(instance.storage))
    os.system(
        f"sudo qemu-img create -f qcow2 -o preallocation=metadata /var/kvm/images/{instance.code}-new.qcow2 {storage}G")
    os.system(f"sudo chown libvirt-qemu:kvm /var/kvm/images/{instance.code}-new.qcow2")

    if instance.os == "ubuntu_20.04":
        os.system(
            f"sudo virt-resize --expand /dev/vda3 /var/kvm/images/{instance.code}.qcow2 /var/kvm/images/{instance.code}-new.qcow2")
    elif instance.os == "centos_8":
        os.system(
            f"sudo virt-resize --expand /dev/vda2 /var/kvm/images/{instance.code}.qcow2 /var/kvm/images/{instance.code}-new.qcow2")

    os.system(f"sudo rm /var/kvm/images/{instance.code}.qcow2")
    os.system(f"sudo mv /var/kvm/images/{instance.code}-new.qcow2 /var/kvm/images/{instance.code}.qcow2")

# def set_vcpus(vcpu,dom):


def set_memory_vcpu(instance, dom, memory=True):
    """
    --->  This function first change the max memory
    --->  Then change the permission to qmeu:kvm
    --->  then expand the vm disk with new image
    --->  then remove old img and rename new image to old name
    :param instance: the instance of model VirtualMachine
    :param dom:
    :param memory:
    :return:
    """

    ram = int(math.fabs(instance.memory))
    vcpus = int(math.fabs(instance.vcpus))
    print("setting memory")
    if memory:
        dom.setMaxMemory(int(ram) * 1024 * 1024)
    if vcpus:
        print(f"setting vcpus {vcpus} active status {dom.isActive()}")
        os.system(f"virsh setvcpus {instance.code} {vcpus} --config --maximum")
        os.system(f"virsh setvcpus {instance.code} {vcpus} --config ")

    dom.create()
    time.sleep(10)
    if memory:
        dom.setMemory(int(ram) * 1024 * 1024)
    # os.system(f"virsh shutdown {instance.code}")

    # os.system(f"virsh start {instance.code}")
    if vcpus:
        print(f"setting vcpus {vcpus}")
        os.system(f"virsh setvcpus --count {vcpus} {instance.code} ")

    print("domain started")
    print("setting memory")

    print("memory set")


def create_vm(instance):

    if instance.os == "ubuntu_20.04":
        command = f"virt-clone --original ubuntu2004 --name {instance.code} --file /var/kvm/images/{instance.code}.qcow2"
    elif instance.os == "centos_8":
        command = f"virt-clone --original centos8 --name {instance.code} --file /var/kvm/images/{instance.code}.qcow2"
    else:
        command = "echo 'invalid option'"

    os.system(command)
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(instance.code)

    if instance.storage > 20:
        print("sending req to set storage")
        set_storage(instance)

    set_memory_vcpu(instance, dom)
    conn.close()
    mac_address = re.search(r"<mac address='([A-Za-z0-9:]+)'", dom.XMLDesc(0)).groups()[0]
    print(f"mac address is {mac_address}")
    instance.mac_address = mac_address
    instance.maintenance = False
    instance.save()


def delete_vm(instance):
    print("deleting vm")

    conn = libvirt.open("qemu:///system")
    try:
        dom = conn.lookupByName(instance.code)
        if dom.isActive():
            os.system(f"virsh shutdown {instance.code}")
            time.sleep(10)
        os.system(f"virsh undefine {instance.code} --remove-all-storage")
    except Exception as e:
        print(e)
    instance.delete()


def update_vm(instance, memory, storage):
    print("updating vm")
    try:
        conn = libvirt.open("qemu:///system")
        dom = conn.lookupByName(instance.code)
        if dom.isActive():
            dom.shutdown()
            time.sleep(20)

        if storage < instance.storage:
            print("updating storage")
            set_storage(instance)
        else:
            print("not updating storage")
            instance.storage = storage
            instance.save()
        print(f'{instance.memory = }')

        if memory != instance.memory:
            print("updating vm memory")
            set_memory_vcpu(instance, dom)
        else:
            print("updating vcpu only")
            set_memory_vcpu(instance, dom, memory=False)

        if not dom.isActive():
            print("this worked")
            dom.create()
            os.system("virsh list --all")
        conn.close()
    except Exception as e:
        print(e)
    finally:
        instance.maintenance = False
        instance.save()
