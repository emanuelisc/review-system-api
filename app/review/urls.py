from django.urls import path, include
from rest_framework.routers import DefaultRouter

from review import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('categories', views.CategoryViewSet)
router.register('reviews', views.ReviewViewSet)
router.register('comments', views.CommentViewSet)

app_name = 'review'

urlpatterns = [
    path('', include(router.urls)),
    path('confirm_review/',
         views.ConfirmReviewView.as_view(), name='confirm_review'),
    path('stat/',
         views.GetReviewStats.as_view(), name='review_stats'),
    path('rating/',
         views.PostRating.as_view(), name='review_rating'),
]
