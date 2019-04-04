from django.urls import path, include
from rest_framework.routers import DefaultRouter

from provider import views


router = DefaultRouter()
router.register('services', views.ServiceViewSet, base_name='services')
router.register('providers', views.ProviderViewSet, base_name='providers')
router.register('admin/services', views.ServiceAdminViewSet,
                base_name='adminservice')
router.register('admin/providers', views.ProviderAdminViewSet,
                base_name='adminprovider')

app_name = 'provider'

urlpatterns = [
    path('', include(router.urls)),
]
