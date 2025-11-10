from rest_framework import serializers
from apps.products.models import Product
from apps.shared.models import Media


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products with translation support"""

    # Translation fields
    title_uz = serializers.CharField(required=True, max_length=255)
    title_en = serializers.CharField(required=False, allow_blank=True, max_length=255)
    title_ru = serializers.CharField(required=False, allow_blank=True, max_length=255)

    description_uz = serializers.CharField(required=True)
    description_en = serializers.CharField(required=False, allow_blank=True)
    description_ru = serializers.CharField(required=False, allow_blank=True)

    # Image upload
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Upload multiple images"
    )

    class Meta:
        model = Product
        fields = [
            'title_uz', 'title_en', 'title_ru',
            'description_uz', 'description_en', 'description_ru',
            'price', 'discount', 'measurement_type',
            'category', 'is_active', 'images'
        ]

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_discount(self, value):
        """Validate discount is between 0-100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100")
        return value

    def create(self, validated_data):
        # Extract fields
        title_uz = validated_data.pop('title_uz')
        title_en = validated_data.pop('title_en', '')
        title_ru = validated_data.pop('title_ru', '')

        description_uz = validated_data.pop('description_uz')
        description_en = validated_data.pop('description_en', '')
        description_ru = validated_data.pop('description_ru', '')

        images = validated_data.pop('images', [])

        # Create product
        product = Product.objects.create(**validated_data)

        # Set translations
        product.title_uz = title_uz
        product.title_en = title_en or title_uz
        product.title_ru = title_ru or title_uz

        product.description_uz = description_uz
        product.description_en = description_en or description_uz
        product.description_ru = description_ru or description_uz

        product.save()

        # Save images
        for image in images:
            Media.objects.create(
                content_object=product,
                file=image,
                media_type='image',
                original_filename=image.name
            )

        return product


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for listing products (without translations)"""
    image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'uuid', 'title', 'description',
            'price', 'real_price', 'discount',
            'measurement_type', 'category',
            'image_url', 'images', 'is_active',
            'created_at'
        ]

    def get_image_url(self, obj):
        """Get first image URL"""
        request = self.context.get('request')
        media = obj.media_files.first()
        if media and request:
            return request.build_absolute_uri(media.file.url)
        elif media:
            return media.file.url
        return None

    def get_images(self, obj):
        """Get all image URLs"""
        request = self.context.get('request')
        images = []
        for media in obj.media_files.all():
            if request:
                images.append(request.build_absolute_uri(media.file.url))
            else:
                images.append(media.file.url)
        return images


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product details with translation support"""
    image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'uuid', 'title', 'description',
            'price', 'real_price', 'discount', 'discount_amount',
            'measurement_type', 'category',
            'image_url', 'images', 'is_active',
            'created_at', 'updated_at'
        ]

    def get_image_url(self, obj):
        """Get first image URL"""
        request = self.context.get('request')
        media = obj.media_files.first()
        if media and request:
            return request.build_absolute_uri(media.file.url)
        elif media:
            return media.file.url
        return None

    def get_images(self, obj):
        """Get all image URLs"""
        request = self.context.get('request')
        images = []
        for media in obj.media_files.all():
            if request:
                images.append(request.build_absolute_uri(media.file.url))
            else:
                images.append(media.file.url)
        return images

    def get_discount_amount(self, obj):
        """Calculate discount amount"""
        if obj.discount > 0:
            return float(obj.price - obj.real_price)
        return 0

    def to_representation(self, instance):
        """Add translation support based on request language"""
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and hasattr(request, 'lang'):
            lang = request.lang.lower()

            # Title translation
            title_field = f'title_{lang}'
            if hasattr(instance, title_field):
                data['title'] = getattr(instance, title_field) or instance.title_uz

            # Description translation
            desc_field = f'description_{lang}'
            if hasattr(instance, desc_field):
                data['description'] = getattr(instance, desc_field) or instance.description_uz

        return data


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating products"""

    # Translation fields (optional for update)
    title_uz = serializers.CharField(required=False, max_length=255)
    title_en = serializers.CharField(required=False, allow_blank=True, max_length=255)
    title_ru = serializers.CharField(required=False, allow_blank=True, max_length=255)

    description_uz = serializers.CharField(required=False)
    description_en = serializers.CharField(required=False, allow_blank=True)
    description_ru = serializers.CharField(required=False, allow_blank=True)

    # Image upload
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'title_uz', 'title_en', 'title_ru',
            'description_uz', 'description_en', 'description_ru',
            'price', 'discount', 'measurement_type',
            'category', 'is_active', 'images'
        ]

    def update(self, instance, validated_data):
        # Extract translation fields
        title_uz = validated_data.pop('title_uz', None)
        title_en = validated_data.pop('title_en', None)
        title_ru = validated_data.pop('title_ru', None)

        description_uz = validated_data.pop('description_uz', None)
        description_en = validated_data.pop('description_en', None)
        description_ru = validated_data.pop('description_ru', None)

        images = validated_data.pop('images', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update translations
        if title_uz:
            instance.title_uz = title_uz
        if title_en is not None:
            instance.title_en = title_en
        if title_ru is not None:
            instance.title_ru = title_ru

        if description_uz:
            instance.description_uz = description_uz
        if description_en is not None:
            instance.description_en = description_en
        if description_ru is not None:
            instance.description_ru = description_ru

        instance.save()

        # Update images (delete old, add new)
        if images is not None:
            instance.media_files.all().delete()
            for image in images:
                Media.objects.create(
                    content_object=instance,
                    file=image,
                    media_type='image',
                    original_filename=image.name
                )

        return instance