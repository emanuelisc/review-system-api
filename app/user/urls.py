from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user import views


router = DefaultRouter()
router.register('users', views.AdminUsersViewSet)
router.register('public', views.PublicViewSet)

router2 = DefaultRouter()
router2.register('', views.PublicViewSet)

app_name = 'user'

urlpatterns = [
    path('admin/', include(router.urls), name='admin'),
    path('public/', include(router2.urls), name='public'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('activate_account/',
         views.ActivateAccountView.as_view(), name='activate_account'),
    path('public/', views.PublicViewSet, name='public'),
]
