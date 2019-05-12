from rest_framework import serializers

from core.models import Provider, ProviderService, ProviderCategory


class ProviderCategorySerializer(serializers.ModelSerializer):
    # Serializer for ingretient object

    class Meta:
        model = ProviderCategory
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ProviderServiceSerializer(serializers.ModelSerializer):
    # Serializer for service object

    class Meta:
        model = ProviderService
        fields = (
            'id',
            'title',
            'description',
            'provider',
            'image',
            'reviews'
        )
        read_only_fields = ('id',)


class ProviderSerializer(serializers.ModelSerializer):
    # Serialize provider

    services = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProviderService.objects.all()
    )

    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProviderCategory.objects.all()
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
            'services',
            'categories',
            'admin_user',
            'reviews'
        )
        read_only_fields = ('id',)


class ProviderDetailSerializer(ProviderSerializer):
    # Serialize a provider details
    services = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


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
