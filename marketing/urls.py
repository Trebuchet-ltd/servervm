
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
router = DefaultRouter()

router.register(r'plans', views.VmPlanViewSet)
router.register(r'request', views.VmRequestAPiViewSet)

router.register(r'marketing', views.MarketingMemberViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'payment/', views.payment)
]
