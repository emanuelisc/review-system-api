from rest_framework import serializers

from core.models import Provider, ProviderService


class ProviderServiceSerializer(serializers.ModelSerializer):
    # Serializer for service object

    class Meta:
        model = ProviderService
        fields = ('id', 'title', 'description', 'provider', 'image')
        read_only_fields = ('id',)


class ProviderSerializer(serializers.ModelSerializer):
    # Serialize provider

    services = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProviderService.objects.all()
    )

    class Meta:
        model = Provider
        fields = (
            'id',
            'title',
            'description',
            'is_active',
            'is_confirmed',
            'image',
            'services'
        )
        read_only_fields = ('id',)


class ProviderDetailSerializer(ProviderSerializer):
    # Serialize a provider details
    services = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # services = ProviderServiceSerializer(many=True, read_only=True)


class ProviderImageSerializer(serializers.ModelSerializer):
    # Serializer for uploading image to provider

    class Meta:
        model = Provider
        fields = ('id', 'image')
        read_only_fields = ('id',)


class ProviderServiceImageSerializer(serializers.ModelSerializer):
    # Serializer for uploading image to service

    class Meta:
        model = ProviderService
        fields = ('id', 'image')
        read_only_fields = ('id',)
