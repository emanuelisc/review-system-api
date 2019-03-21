from django.urls import path, include
from rest_framework.routers import DefaultRouter

from page import views


router = DefaultRouter()
router.register('categories', views.CategoryViewSet, base_name='categories')
router.register('pages', views.PageViewSet, base_name='pages')
router.register('admin/categories', views.CategoryAdminViewSet,
                base_name='admincat')
router.register('admin/pages', views.PageAdminViewSet,
                base_name='adminpages')

app_name = 'page'

urlpatterns = [
    path('', include(router.urls)),
]
