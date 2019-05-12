from rest_framework import serializers

from core.models import Review, ReviewCategory, HashTag, Comment
from user.serializers import UserSerializer


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


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    reply_set = RecursiveSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'review', 'date', 'content', 'parent',
                  'rating', 'user', 'is_provider', 'reply_set')


class ReviewSerializer(serializers.ModelSerializer):
    # Serialize a recipe

    # categories = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     queryset=ReviewCategory.objects.all(),
    #     required=False
    # )
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ReviewCategory.objects.all(),
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=HashTag.objects.all(),
        required=False
    )
    user = UserSerializer(read_only=True)

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
