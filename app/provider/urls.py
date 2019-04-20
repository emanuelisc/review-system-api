from django.urls import path, include
from rest_framework.routers import DefaultRouter

from provider import views


router = DefaultRouter()
router.register('services', views.ServiceViewSet, base_name='services')
router.register('providers', views.ProviderViewSet, base_name='providers')
router.register('categories', views.CategoryViewSet, base_name='categories')
router.register('own/services', views.ServiceOwnerViewSet,
                base_name='ownservices')
router.register('own/provider', views.ProviderOwnerViewSet,
                base_name='ownprovider')


app_name = 'provider'

urlpatterns = [
    path('', include(router.urls)),
]
