from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics, authentication, \
    permissions, viewsets, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
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

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'me': {
                'email': user.email,
                'name': user.name,
                'is_staff': user.is_staff,
                'is_company': user.is_company
            }
        })


class ManageUserView(generics.RetrieveUpdateAPIView):

    """
    Return a list of all the existing users.
    """
    # Manage the authenticated user
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        # Retrieve and return authenticated user
        return self.request.user

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # Upload an image to a page
        user = self.request.user()
        serializer = self.get_serializer(
            user,
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
        return queryset.all().order_by('id')

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # Upload an image to a page
        user = self.request.user()
        serializer = self.get_serializer(
            user,
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
