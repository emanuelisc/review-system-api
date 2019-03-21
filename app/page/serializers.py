from rest_framework import serializers

from core.models import Page, PageCategory


class PageCategorySerializer(serializers.ModelSerializer):
    # Serializer for ingretient object

    class Meta:
        model = PageCategory
        fields = ('id', 'name')
        read_only_fields = ('id',)


class PageSerializer(serializers.ModelSerializer):
    # Serialize a recipe

    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=PageCategory.objects.all()
    )

    class Meta:
        model = Page
        fields = (
            'id',
            'title',
            'text',
            'slug',
            'categories',
            'image'
        )
        read_only_fields = ('id',)


class PageDetailSerializer(PageSerializer):
    # Serialize a page details
    categories = PageCategorySerializer(many=True, read_only=True)


class PageImageSerializer(serializers.ModelSerializer):
    # Serializer for uploading image to page

    class Meta:
        model = Page
        fields = ('id', 'image')
        read_only_fields = ('id',)
