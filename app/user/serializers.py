from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class PublicUserSerializer(serializers.ModelSerializer):
    # Serializer for public user info access
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'name',
                  'is_company', 'image')


class UserSerializer(serializers.ModelSerializer):
    # Serializer for the users object

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'password', 'name',
                  'is_confirmed', 'is_company', 'is_staff', 'image')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        read_only_fields = ('is_confirmed', 'is_company', 'is_staff',)

    def create(self, validated_data):
        # Create a new user with encrypted password and return it
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # Update a user, setting the password correctly and return it
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

            return user


class AuthTokenSerializer(serializers.Serializer):
    # Serializer for the user authentication object
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        # Validate and authenticate the user
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code=authenticate)

        attrs['user'] = user
        return attrs


class AdminUsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'email',
            'password',
            'name',
            'is_staff',
            'is_company',
            'is_active',
            'is_confirmed',
            'provider_id',
            'image'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        # Update a user, setting the password correctly and return it
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            # print(password)
            user.set_password(password)
            user.save()
            return user
        else:
            user.save()
            return user
        
    def create(self, validated_data):
        # Create a new user with encrypted password and return it
        return get_user_model().objects.create_user(**validated_data)


class UserImageSerializer(serializers.ModelSerializer):
    # Serializer for uploading image to provider

    class Meta:
        model = get_user_model()
        fields = ('id', 'image')
        read_only_fields = ('id',)
