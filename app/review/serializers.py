from rest_framework import serializers

from core.models import Review, ReviewCategory, HashTag


class TagSerializer(serializers.ModelSerializer):
    # Serializer for tag objects

    class Meta:
        model = HashTag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    # Serializer for category object

    class Meta:
        model = ReviewCategory
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ReviewSerializer(serializers.ModelSerializer):
    # Serialize a recipe

    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ReviewCategory.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=HashTag.objects.all()
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'title',
            'description',
            'rating',
            'categories',
            'tags',
            'date',
            'is_auto_confirmed',
            'confirmation_text',
            'is_confirmed',
            'image',
            'user'
        )
        read_only_fields = ('id',)


class ReviewDetailSerializer(ReviewSerializer):
    # Serialize a review details
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class ReviewImageSerializer(serializers.ModelSerializer):
    # Serializer for uploading image to recipes

    class Meta:
        model = Review
        fields = ('id', 'image')
        read_only_fields = ('id',)
