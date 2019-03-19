# from rest_framework.decorators import action
# from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# from django.core.exceptions import ValidationError

from core.models import Page, PageCategory
from page import serializers


class CategoryAdminViewSet(viewsets.ModelViewSet):
    # Viewset for page attributes
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)
    queryset = PageCategory.objects.all()
    serializer_class = serializers.PageCategorySerializer

    def get_queryset(self):
        # Return objects for the current authenticated user only
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(page__isnull=False)

        return queryset.all().order_by('-name').distinct()

    def perform_create(self, serializer):
        # Create a new object
        serializer.save()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    # Viewset for page attributes
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
    serializer_class = serializers.PageSerializer
    queryset = Page.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

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

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new serializer
        serializer.save()
