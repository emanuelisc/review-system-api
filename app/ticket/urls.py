from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ticket import views


router = DefaultRouter()
router.register('tickets', views.TicketViewSet, base_name='tickets')
router.register('admin', views.TicketAdminViewSet, base_name='admin')

app_name = 'ticket'

urlpatterns = [
    path('', include(router.urls)),
]
