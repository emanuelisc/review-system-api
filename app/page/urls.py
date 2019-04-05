from django.urls import path, include
from rest_framework.routers import DefaultRouter

from page import views


router = DefaultRouter()
router.register('categories', views.CategoryViewSet, base_name='categories')
router.register('pages', views.PageViewSet, base_name='pages')

app_name = 'page'

urlpatterns = [
    path('', include(router.urls)),
]
