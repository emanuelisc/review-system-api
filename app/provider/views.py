from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.models import Provider, ProviderService
from provider import serializers


class ServiceAdminViewSet(viewsets.ModelViewSet):
    # Viewset for provider service attributes -> admin
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)
    queryset = ProviderService.objects.all()
    serializer_class = serializers.ProviderServiceSerializer

    def get_queryset(self):
        # Return objects for the current authenticated user only
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(provider__isnull=False)

        return queryset.all().order_by('-title').distinct()

    def perform_create(self, serializer):
        # Create a new object
        serializer.save()


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    # Viewset for provider service attributes -> public
    queryset = ProviderService.objects.all()
    serializer_class = serializers.ProviderServiceSerializer

    def get_queryset(self):
        # Return objects
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(provider__isnull=False)

        return queryset.all().order_by('-title').distinct()


class ProviderViewSet(viewsets.ReadOnlyModelViewSet):
    # Manage page in the database
    serializer_class = serializers.ProviderSerializer
    queryset = Provider.objects.all()

    def _params_to_ints(self, qs):
        # Convert a list of string IDs to a list of integers
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        # Retrieve pages
        services = self.request.query_params.get('services')
        queryset = self.queryset
        if services:
            service_ids = self._params_to_ints(services)
            queryset = queryset.filter(services__id__in=service_ids)

        return queryset.filter()

    def get_serializer_class(self):
        # Return appropriate serializer class
        if self.action == 'retrieve':
            return serializers.ProviderDetailSerializer
        elif self.action == 'upload_image':
            return serializers.ProviderImageSerializer

        return self.serializer_class


class ProviderAdminViewSet(viewsets.ModelViewSet):
    # Manage recipes in the database
    serializer_class = serializers.ProviderSerializer
    queryset = Provider.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def _params_to_ints(self, qs):
        # Convert a list of string IDs to a list of integers
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        # Retrieve the pages for the authenticated user
        services = self.request.query_params.get('services')
        queryset = self.queryset
        if services:
            service_ids = self._params_to_ints(services)
            queryset = queryset.filter(services__id__in=service_ids)

        return queryset.all().distinct()

    def get_serializer_class(self):
        # Return appropriate serializer class
        if self.action == 'retrieve':
            return serializers.ProviderDetailSerializer
        elif self.action == 'upload_image':
            return serializers.ProviderImageSerializer

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
