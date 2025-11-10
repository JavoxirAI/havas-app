from rest_framework import serializers
from apps.products.models import Product
from apps.recipes.models import Recipe, RecipeProduct, RecipeStep
from apps.shared.models import Media


class RecipeProductSerializer(serializers.ModelSerializer):
    """Serializer for recipe ingredients"""
    product_id = serializers.IntegerField(write_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_title_uz = serializers.CharField(source='product.title_uz', read_only=True)
    product_title_en = serializers.CharField(source='product.title_en', read_only=True)
    product_title_ru = serializers.CharField(source='product.title_ru', read_only=True)
    measurement_type = serializers.CharField(source='product.measurement_type', read_only=True)

    class Meta:
        model = RecipeProduct
        fields = [
            'id', 'product_id', 'product_title',
            'product_title_uz', 'product_title_en', 'product_title_ru',
            'quantity', 'measurement_type', 'is_optional', 'order'
        ]
        read_only_fields = ['id']


class RecipeStepSerializer(serializers.ModelSerializer):
    """Serializer for recipe steps"""
    media_url = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = RecipeStep
        fields = [
            'id', 'step_number', 'title', 'description',
            'duration_minutes', 'tips', 'media_url', 'progress_percentage'
        ]
        read_only_fields = ['id']

    def get_media_url(self, obj):
        """Get media URL for step"""
        request = self.context.get('request')
        media = obj.media_files.first()
        if media and request:
            return request.build_absolute_uri(media.file.url)
        elif media:
            return media.file.url
        return None

    def get_progress_percentage(self, obj):
        """Calculate progress percentage based on total steps"""
        total_steps = obj.recipe.steps.count()
        if total_steps > 0:
            return round((obj.step_number / total_steps) * 100, 1)
        return 0


class RecipeListSerializer(serializers.ModelSerializer):
    """List view - basic recipe info"""
    image_url = serializers.SerializerMethodField()
    ingredients_count = serializers.IntegerField(source='ingredients.count', read_only=True)
    steps_count = serializers.IntegerField(source='steps.count', read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'uuid', 'name', 'description', 'image_url',
            'rating', 'calories', 'time_minutes', 'difficulty', 'servings',
            'ingredients_count', 'steps_count', 'view_count',
            'created_at'
        ]

    def get_image_url(self, obj):
        """Get main recipe image"""
        request = self.context.get('request')
        media = obj.media_files.first()
        if media and request:
            return request.build_absolute_uri(media.file.url)
        elif media:
            return media.file.url
        return None

    def to_representation(self, instance):
        """Add translation support"""
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and hasattr(request, 'lang'):
            lang = request.lang.lower()
            name_field = f'name_{lang}'
            if hasattr(instance, name_field):
                data['name'] = getattr(instance, name_field) or instance.name_uz

            desc_field = f'description_{lang}'
            if hasattr(instance, desc_field):
                data['description'] = getattr(instance, desc_field) or instance.description_uz

        return data


class RecipeDetailSerializer(RecipeListSerializer):
    """Detail view - full recipe with ingredients and steps"""
    ingredients = RecipeProductSerializer(many=True, read_only=True)
    steps = RecipeStepSerializer(many=True, read_only=True)
    total_duration = serializers.SerializerMethodField()

    class Meta(RecipeListSerializer.Meta):
        fields = RecipeListSerializer.Meta.fields + [
            'ingredients', 'steps', 'total_duration'
        ]

    def get_total_duration(self, obj):
        """Calculate total duration including all steps"""
        steps_duration = sum(step.duration_minutes for step in obj.steps.all())
        return obj.time_minutes + steps_duration


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update recipes with nested ingredients and steps"""
    ingredients = RecipeProductSerializer(many=True)
    steps = RecipeStepSerializer(many=True)
    image = serializers.ImageField(write_only=True, required=False)

    # Translation fields
    name_uz = serializers.CharField(required=True, max_length=255)
    name_en = serializers.CharField(required=False, allow_blank=True, max_length=255)
    name_ru = serializers.CharField(required=False, allow_blank=True, max_length=255)

    description_uz = serializers.CharField(required=False, allow_blank=True)
    description_en = serializers.CharField(required=False, allow_blank=True)
    description_ru = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Recipe
        fields = [
            'name_uz', 'name_en', 'name_ru',
            'description_uz', 'description_en', 'description_ru',
            'image', 'rating', 'calories', 'time_minutes',
            'difficulty', 'servings', 'ingredients', 'steps'
        ]

    def validate_ingredients(self, value):
        """Validate ingredients exist"""
        if not value:
            raise serializers.ValidationError("At least one ingredient is required")

        product_ids = [item['product_id'] for item in value]
        existing_products = Product.objects.filter(id__in=product_ids, is_active=True)

        if existing_products.count() != len(product_ids):
            raise serializers.ValidationError("Some products do not exist or are inactive")

        return value

    def validate_steps(self, value):
        """Validate steps"""
        if not value:
            raise serializers.ValidationError("At least one step is required")

        step_numbers = [step['step_number'] for step in value]
        if len(step_numbers) != len(set(step_numbers)):
            raise serializers.ValidationError("Step numbers must be unique")

        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        steps_data = validated_data.pop('steps', [])
        image = validated_data.pop('image', None)

        # Extract translation fields
        name_uz = validated_data.pop('name_uz')
        name_en = validated_data.pop('name_en', '')
        name_ru = validated_data.pop('name_ru', '')

        description_uz = validated_data.pop('description_uz', '')
        description_en = validated_data.pop('description_en', '')
        description_ru = validated_data.pop('description_ru', '')

        # Create recipe
        recipe = Recipe.objects.create(**validated_data)

        # Set translations
        recipe.name_uz = name_uz
        recipe.name_en = name_en or name_uz
        recipe.name_ru = name_ru or name_uz

        recipe.description_uz = description_uz
        recipe.description_en = description_en or description_uz
        recipe.description_ru = description_ru or description_uz

        recipe.save()

        # Save image
        if image:
            Media.objects.create(
                content_object=recipe,
                file=image,
                media_type='image',
                original_filename=image.name
            )

        # Create ingredients
        for item in ingredients_data:
            product_id = item.pop('product_id')
            RecipeProduct.objects.create(
                recipe=recipe,
                product_id=product_id,
                **item
            )

        # Create steps
        for step in steps_data:
            RecipeStep.objects.create(recipe=recipe, **step)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        steps_data = validated_data.pop('steps', None)
        image = validated_data.pop('image', None)

        # Extract translation fields
        name_uz = validated_data.pop('name_uz', None)
        name_en = validated_data.pop('name_en', None)
        name_ru = validated_data.pop('name_ru', None)

        description_uz = validated_data.pop('description_uz', None)
        description_en = validated_data.pop('description_en', None)
        description_ru = validated_data.pop('description_ru', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update translations
        if name_uz:
            instance.name_uz = name_uz
        if name_en:
            instance.name_en = name_en
        if name_ru:
            instance.name_ru = name_ru

        if description_uz:
            instance.description_uz = description_uz
        if description_en:
            instance.description_en = description_en
        if description_ru:
            instance.description_ru = description_ru

        instance.save()

        # Update image
        if image:
            instance.media_files.all().delete()
            Media.objects.create(
                content_object=instance,
                file=image,
                media_type='image',
                original_filename=image.name
            )

        # Update ingredients
        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for item in ingredients_data:
                product_id = item.pop('product_id')
                RecipeProduct.objects.create(
                    recipe=instance,
                    product_id=product_id,
                    **item
                )

        # Update steps
        if steps_data is not None:
            instance.steps.all().delete()
            for step in steps_data:
                RecipeStep.objects.create(recipe=instance, **step)

        return instance
