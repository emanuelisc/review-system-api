import datetime
import json

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from core.models import Review, ReviewCategory, \
    HashTag, User, ValidationToken, \
    Comment, ReviewLog, RatingLog
from core.permissions import ReadOnly
from core.logging import ReviewLogging
from review import serializers, filter_request


class BaseReviewAttrViewSet(viewsets.ModelViewSet):
    # Base viewset for review attributes
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated | ReadOnly,)

    def get_queryset(self):
        # Return objects for the current authenticated user only
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.all().order_by('-name').distinct()


class TagViewSet(BaseReviewAttrViewSet):
    # Manage tags in the database
    queryset = HashTag.objects.all()
    serializer_class = serializers.TagSerializer


class CategoryViewSet(BaseReviewAttrViewSet):
    # Manage categories in the database
    queryset = ReviewCategory.objects.all()
    serializer_class = serializers.CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):
    # queryset = Comment.objects.filter(parent=None) # Don't
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated | ReadOnly,)

    def get_queryset(self):
        review = self.request.query_params.get('review')
        queryset = self.queryset.filter(parent=None)
        if review:
            queryset = queryset.filter(review__id=int(review))
        return queryset.filter()

    def perform_create(self, serializer):
        # Create a new serializer
        serializer.validated_data['user'] = self.request.user
        serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
        # Manage reviews in the database
    serializer_class = serializers.ReviewSerializer
    queryset = Review.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated | ReadOnly,)

    def _params_to_ints(self, qs):
            # Convert a list of string IDs to a list of integers
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        # Retrieve the reviews
        tags = self.request.query_params.get('tags')
        categories = self.request.query_params.get('categories')
        queryset = self.queryset
        user_id = int(self.request.query_params.get('user_id', 0))
        ReviewLogging.log_get(self, self.request)
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if categories:
            category_ids = self._params_to_ints(categories)
            queryset = queryset.filter(categories__id__in=category_ids)
        if user_id == 0:
            return queryset.all()
        elif user_id == -1:
            queryset.filter(user_id=self.request.user.id)
        return queryset.filter(user_id=user_id)

    def get_serializer_class(self):
        # Return appropriate serializer class
        if self.action == 'retrieve':
            return serializers.ReviewDetailSerializer
        elif self.action == 'upload_image':
            return serializers.ReviewImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new serializer
        title = serializer.validated_data['title']
        text = serializer.validated_data['description']
        validation = filter_request.make_request(title, text)
        if validation['results'] == 0:
            serializer.validated_data['is_auto_confirmed'] = False
        else:
            serializer.validated_data['is_auto_confirmed'] = True
        serializer.validated_data['confirmation_text'] \
            = validation['probability']
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.is_staff is True:
            serializer.save()
        elif serializer.validated_data['user'] != self.request.user:
            raise PermissionDenied('You cannot update this object!')
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.is_staff is True:
            instance.delete()
        elif instance.user_id != self.request.user.id:
            raise PermissionDenied('You cannot delete this object!')
        else:
            instance.delete()

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # Upload an image to a recipe
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['POST'], detail=False, url_path='check')
    def checkReview(self, request, pk=None):
        # check review
        print(request.data['title'])
        validation = filter_request.make_request(
            request.data['title'], request.data['text'])
        if validation:
            return Response(
                validation,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                "Bad data",
                status=status.HTTP_400_BAD_REQUEST
            )


class PostRating(generics.RetrieveAPIView):
    def get(self, serializer):
        # user = self.request.user
        user = self.request.query_params.get('user', None)
        review_id = self.request.query_params.get('id', None)
        value = self.request.query_params.get('val', None)
        if user and review_id:
            review = Review.objects.filter(id=review_id).first()
            if review == None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            review_rating_logs = RatingLog.objects.filter(review_id=review_id)
            can_add = review_rating_logs.filter(user_id=user)
            if can_add:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if value == '1':
                review.rating = review.rating - 1
            else:
                review.rating = review.rating + 1
            review.save()
            RatingLog.objects.create(review_id=review_id, user_id=user)
            return Response(
                {'success': 'Rating added'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No user specified'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class GetReviewStats(generics.RetrieveAPIView):
    def get(self, serializer):
        interval = self.request.query_params.get('interval', None)
        review_id = self.request.query_params.get('id', None)
        if review_id == None:
            return Response(
                {'error': 'No review id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        logs = ReviewLog.objects.filter(review_id=review_id)
        if interval:
            data = {}
            for i in range(int(interval)):
                newDate = datetime.date.today() - datetime.timedelta(days=i)
                data[str(newDate)] = logs.filter(date=newDate).count()
            return Response(
                data,
                status=status.HTTP_200_OK
            )
        else:
            data = {}
            for i in range(3):
                newDate = datetime.date.today() - datetime.timedelta(days=i)
                data[str(newDate)] = logs.filter(date=newDate).count()
            return Response(
                data,
                status=status.HTTP_200_OK
            )


class ConfirmReviewView(generics.RetrieveAPIView):
    def get(self, serializer):
        email = self.request.query_params.get('email', None)
        token = self.request.query_params.get('token', None)
        review_id = self.request.query_params.get('review', None)
        if email or review_id or token:
            try:
                token_obj = ValidationToken.objects.get(token=token)
                try:
                    user = User.objects.get(email=str(email))
                    user.is_confirmed = True
                    user.save()
                    try:
                        review = Review.objects.get(id=int(review_id))
                        review.is_anon = False
                        review.save()
                        token_obj.delete()
                        return Response(
                            {'Aktyvuota'},
                            status=status.HTTP_200_OK
                        )
                    except Review.DoesNotExist:
                        return Response(None, status=status.HTTP_404_NOT_FOUND)
                except User.DoesNotExist:
                    return Response(None, status=status.HTTP_404_NOT_FOUND)
            except ValidationToken.DoesNotExist:
                return Response(None, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
