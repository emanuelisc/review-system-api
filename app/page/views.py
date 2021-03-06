from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser

from core.models import Page, PageCategory
from core.permissions import ReadOnly
from page import serializers


class CategoryViewSet(viewsets.ModelViewSet):
    # Viewset for page attributes
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser | ReadOnly,)
    queryset = PageCategory.objects.all()
    serializer_class = serializers.PageCategorySerializer

    def get_queryset(self):
        # Return objects
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(page__isnull=False)

        return queryset.all().order_by('-name').distinct()


class PageViewSet(viewsets.ModelViewSet):
    # Manage page in the database
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser | ReadOnly,)
    serializer_class = serializers.PageSerializer
    queryset = Page.objects.all()

    def _params_to_ints(self, qs):
        # Convert a list of string IDs to a list of integers
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        # Retrieve pages
        categories = self.request.query_params.get('categories')
        queryset = self.queryset
        if categories:
            category_ids = self._params_to_ints(categories)
            queryset = queryset.filter(categories__id__in=category_ids)

        return queryset.filter()

    def get_serializer_class(self):
        # Return appropriate serializer class
        if self.action == 'retrieve':
            return serializers.PageDetailSerializer
        elif self.action == 'upload_image':
            return serializers.PageImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new serializer
        serializer.save()

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # Upload an image to a page
        page = self.get_object()
        serializer = self.get_serializer(
            page,
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
