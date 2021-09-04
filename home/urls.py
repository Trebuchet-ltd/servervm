from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VmViewSet

# Setup the URLs and include login URLs for the browsable API.
router = DefaultRouter()

router.register(r"virtual_machines", VmViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
]