from rest_framework import serializers

from apps.products.models import Product
from apps.shared.mixins.translation_mixins import (
    TranslatedFieldsWriteMixin,
    TranslatedFieldsReadMixin
)


class ProductTranslationMixin:
    """Shared configuration for OnBoarding serializers"""
    translatable_fields = ['title', 'description', 'images']
    media_fields = ['images']


class ProductCreateSerializer(ProductTranslationMixin, TranslatedFieldsWriteMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'measurement_type',
                  'is_active', 'category', 'discount']

    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     if request and hasattr(request, 'user'):
    #         validated_data['created_by'] = request.user
    #     return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['title', 'description']


class ProductDetailSerializer(ProductTranslationMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'uuid', 'title', 'description',
                  'price', 'real_price', 'measurement_type',
                  'created_at', 'is_active', 'category', 'discount']
