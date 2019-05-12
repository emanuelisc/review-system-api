from rest_framework.response import Response
from rest_framework import generics, authentication, permissions, viewsets, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, \
    AuthTokenSerializer, \
    AdminUsersSerializer

from core.models import User, ValidationToken
from user.mail import ValidateEmail


class ActivateAccountView(generics.RetrieveAPIView):
    def get(self, serializer):
        email = self.request.query_params.get('email', '')
        token = self.request.query_params.get('token', '')
        if email or token:
            try:
                token_obj = ValidationToken.objects.get(token=token)
                try:
                    user = User.objects.get(email=str(email))
                    user.is_confirmed = True
                    user.save()
                    token_obj.delete()
                    return Response(
                        {'Aktyvuota'},
                        status=status.HTTP_200_OK
                    )
                except User.DoesNotExist:
                    return Response(None, status=status.HTTP_404_NOT_FOUND)
            except ValidationToken.DoesNotExist:
                return Response(None, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(None, status=status.HTTP_404_NOT_FOUND)


class CreateUserView(generics.CreateAPIView, ValidateEmail):
    # Create a new user in the system
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        # Create a new serializer

        mail_address = serializer.validated_data['email']
        name = serializer.validated_data['name']
        if mail_address:
            ValidateEmail.send_confirmation(self, mail_address, name)
        serializer.save()


class CreateTokenView(ObtainAuthToken):
    # Create a new auth token for user
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    # Manage the authenticated user
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        # Retrieve and return authenticated user
        return self.request.user


class AdminUsersViewSet(viewsets.ModelViewSet):
    # Manage recipes in the database
    serializer_class = AdminUsersSerializer
    queryset = User.objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    def _params_to_ints(self, qs):
        # Convert a list of string IDs to a list of integers
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        queryset = self.queryset
        return queryset.all()
