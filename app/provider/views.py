from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied

from core.models import Provider, ProviderService, ProviderCategory
from core.permissions import ReadOnly, IsCompany
from core.request_log.mixins import RequestLogViewMixin
from provider import serializers


class CategoryViewSet(viewsets.ModelViewSet):
    # Viewset for page attributes
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser | ReadOnly,)
    queryset = ProviderCategory.objects.all()
    serializer_class = serializers.ProviderCategorySerializer

    def get_queryset(self):
        # Return objects
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(page__isnull=False)

        return queryset.all().order_by('-name').distinct()


class ServiceOwnerViewSet(viewsets.ModelViewSet, RequestLogViewMixin):
    # Viewset for editing and creating services for provider
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated & IsCompany, )
    queryset = ProviderService.objects.all()
    serializer_class = serializers.ProviderServiceSerializer

    def get_queryset(self):
        # Return objects
        queryset = self.queryset
        if self.request.user.provider_id:
            return queryset.filter(provider=self.request.user.provider_id)
        raise PermissionDenied('You are not part of any provider!')

    def perform_create(self, serializer):
        # Create a new object
        if self.request.user.provider_id:
            serializer.save(provider=self.request.user.provider_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        raise PermissionDenied('You are not part of any provider!')


class ServiceViewSet(viewsets.ModelViewSet):
    # Viewset for provider service attributes
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser | ReadOnly,)
    queryset = ProviderService.objects.all()
    serializer_class = serializers.ProviderServiceSerializer

    def get_queryset(self):
        # Return objects
        queryset = self.queryset
        return queryset.all().order_by('-title').distinct()


class ProviderOwnerViewSet(viewsets.ModelViewSet, RequestLogViewMixin):
    # Viewset for Provider
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated & IsCompany,)
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

        if self.request.user.provider_id:
            return queryset.filter(id=self.request.user.provider_id_id)
        else:
            return queryset.filter(admin_user=self.request.user)

    def get_serializer_class(self):
        # Return appropriate serializer class
        if self.action == 'retrieve':
            serializer = serializers.ProviderDetailSerializer
            return serializer
        elif self.action == 'upload_image':
            return serializers.ProviderImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new object
        if self.request.user.provider_id:
            raise PermissionDenied('You are already part of organization!')
        serializer.save(admin_user=self.request.user)
        user = self.request.user
        if user.id == serializer.data['admin_user']:
            user.provider_id_id = serializer.data['id']
            user.save()

    def perform_destroy(self, instance):
        # Do not permit deleting
        raise PermissionDenied('Organization cannot be deleted!')

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


class ProviderViewSet(viewsets.ModelViewSet, RequestLogViewMixin):
    # Viewset for Provider
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated | ReadOnly,)
    serializer_class = serializers.ProviderSerializer
    queryset = Provider.objects.all()

    def _params_to_ints(self, qs):
        # Convert a list of string IDs to a list of integers
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        # Retrieve pages
        services = self.request.query_params.get('services')
        categories = self.request.query_params.get('categories')
        queryset = self.queryset
        # print(self.request.META['REMOTE_ADDR'] + ' Testas3\n')

        if services:
            service_ids = self._params_to_ints(services)
            queryset = queryset.filter(services__id__in=service_ids)
        if categories:
            category_ids = self._params_to_ints(categories)
            queryset = queryset.filter(categories__id__in=category_ids)

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
