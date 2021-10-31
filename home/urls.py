from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
# Setup the URLs and include login URLs for the browsable API.
router = DefaultRouter()

router.register(r"virtual_machines", views.VmViewSet)
router.register(r'pem_file', views.PemFileViewSet)


urlpatterns = [
    path(r'', include(router.urls)),
]
