import random
import threading

import libvirt
import re
import os
import time
import logging
import math
import requests
from requests.auth import HTTPBasicAuth
import servervm.settings as settings
import hmac
import hashlib
import string
from .models import VirtualMachine
from marketing.models import VmRequest
logger = logging.getLogger("home")


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
        command = f"virt-clone --original ubuntu2004_base --name {instance.code} --file /var/kvm/images/{instance.code}.qcow2"
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


def verify_signature(request):
    logger.info("Signature verification taking place")
    try:
        signature_payload = request.GET['razorpay_payment_link_id'] + '|' + \
                            request.GET['razorpay_payment_link_reference_id'] + '|' + \
                            request.GET['razorpay_payment_link_status'] + '|' + \
                            request.GET['razorpay_payment_id']
        signature_payload = bytes(signature_payload, 'utf-8')
        byte_key = bytes(settings.razorpay_key_secret, 'utf-8')
        generated_signature = hmac.new(byte_key, signature_payload, hashlib.sha256).hexdigest()
        if generated_signature == request.GET["razorpay_signature"]:
            logger.info("Signature verification successfully completed")
            return True
        else:
            logger.warning("signature verification failed")
            return False
    except ValueError:
        logger.warning("signature verification failed value error")
        return False
    except Exception as e:
        logger.warning("signature verification failed")
        logger.warning(e)
        return False


def new_id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """ This function generate a random string  """

    return ''.join(random.choice(chars) for _ in range(size))


def create_new_unique_id():
    """ This function verify the uniqueness of an id for transaction """

    not_unique = True
    unique_id = new_id_generator()
    while not_unique:
        unique_id = new_id_generator()
        if not VmRequest.objects.filter(transaction_id=unique_id):
            not_unique = False
    return str(unique_id)


def get_payment_link(user, vm_request):
    """
    This Function returns thr payment url for that particular checkout
    Returns a list with payment link and payment id created by razorpay
    """
    logger.info(f"{user} Requesting to get payment link ")
    key_secret = settings.razorpay_key_secret
    call_back_url = settings.webhook_call_back_url
    key_id = settings.razorpay_key_id
    transaction_id = create_new_unique_id()
    vm_request.transaction_id = transaction_id
    amount = vm_request.month * vm_request.plan.amount
    vm_request.save()
    logger.info(f"created transaction details object for {user}")
    amount *= 100  # converting rupees to paisa

    try:
        url = 'https://api.razorpay.com/v1/payment_links'

        data = {
            "amount": amount,
            "currency": "INR",
            "callback_url": call_back_url,
            "callback_method": "get",
            'reference_id': transaction_id,
            "customer": {
                "email": user.email,
                "name": user.username
            },
            "options": {
                "checkout": {
                    "name": "DreamEat",
                    "prefill": {
                        "email": user.email,
                    },
                    "readonly": {
                        "email": True,
                        "contact": True
                    }
                }
            }
        }
        res = requests.post(url,
                            json=data,
                            headers={'Content-type': 'application/json'},
                            auth=HTTPBasicAuth(key_id, key_secret)).json()
        try:
            logger.info(f"Razorpay response object {res} ")
            vm_request.payment_id = res.get("id")
            logger.info(f" Transaction id {res.get('id')} ,  status = {res.get('status')}")
            vm_request.payment_status = res.get("status")
            payment_url = res.get('short_url')
            vm_request.payment_link = payment_url
            logger.info(f"now created transaction details is {vm_request}")

            logger.info(f"payment url - {payment_url}")
            vm_request.save()
            return payment_url

        except KeyError:
            logger.warning(f"payment link creation failed ... {res} ")
            return False
    except Exception as e:
        logger.warning(e)
        return False


def handle_payment(transaction_id):
    vm_request = VmRequest.objects.get(transaction_id=transaction_id)

    vm_plan = vm_request.plan

    vm = VirtualMachine.objects.create(
        user=vm_request.user,
        memory=vm_plan.memory,
        vcpus=vm_plan.vcpus,
        storage=vm_plan.storage,
        os=vm_plan.os,
        pem_file=vm_request.pem_file,
        plan=vm_plan
    )
    threading.Thread(target=create_vm, args=(vm,)).start()
