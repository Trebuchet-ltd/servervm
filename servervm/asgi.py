"""
ASGI config for servervm project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django

from django.core.asgi import get_asgi_application

from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter

django.setup()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servervm.settings')

application = ProtocolTypeRouter({
  "http": AsgiHandler(),

    })



