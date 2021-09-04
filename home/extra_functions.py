import libvirt
import re
import pexpect
import os


def create_vm(instance, ram=4,):
    command = f"virt-clone --original ubuntu2004 --name {instance.name} --file /var/kvm/images/{instance.name}.img"
    os.system(command)
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(instance.name)
    if ram != 4:
        dom.setMaxMemory(int(ram) * 1024 * 1024)
        dom.setMemory(int(ram) * 1024 * 1024)
    conn.close()
    mac_address = re.search(r"<mac address='([A-Za-z0-9:]+)'", dom.XMLDesc(0)).groups()
    instance.mac_address = mac_address
    instance.save()
