from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from core.models import Review, ReviewCategory, HashTag, User, ValidationToken
from core.permissions import ReadOnly
from review import serializers


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
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if categories:
            category_ids = self._params_to_ints(categories)
            queryset = queryset.filter(categories__id__in=category_ids)

        if user_id == 0:
            return queryset.all()
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
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data['user'] != self.request.user:
            raise PermissionDenied('You cannot update this object!')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied('You cannot delete this object!')
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


class AnonReviewViewSet(viewsets.ModelViewSet):
    # Manage reviews in the database
    serializer_class = serializers.ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        # Retrieve the reviews
        queryset = self.queryset
        return queryset.all()

    def get_serializer_class(self):
        # Return appropriate serializer class
        if self.action == 'retrieve':
            return serializers.ReviewDetailSerializer
        elif self.action == 'upload_image':
            return serializers.ReviewImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new serializer
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        raise PermissionDenied('You cannot update this object!')

    def perform_destroy(self, instance):
        raise PermissionDenied('You cannot delete this object!')

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
