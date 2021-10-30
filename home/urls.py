from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
# Setup the URLs and include login URLs for the browsable API.
router = DefaultRouter()

router.register(r"virtual_machines", views.VmViewSet)
router.register(r'pem_file', views.PemFileViewSet)
router.register(r'plans', views.VmPlanViewSet)
router.register(r'request', views.VmRequestAPiViewSet)
urlpatterns = [
    path(r'', include(router.urls)),
    path(r'payment/', views.payment)
]
