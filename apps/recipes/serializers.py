from rest_framework import serializers
from apps.products.models import Product
from apps.recipes.models import RecipeProduct, RecipeStep, Recipe


class RecipeProductSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = RecipeProduct
        fields = ['id', 'product', 'product_name', 'quantity']


class RecipeStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeStep
        fields = ['id', 'step_number', 'text']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeProductSerializer(many=True, read_only=True)
    steps = RecipeStepSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'image',
            'rating', 'calories', 'time_minutes',
            'ingredients', 'steps',
            'created_at', 'updated_at'
        ]


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeProductSerializer(many=True, write_only=True)
    steps = RecipeStepSerializer(many=True, write_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'image',
            'rating', 'calories', 'time_minutes',
            'ingredients', 'steps'
        ]

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        steps_data = validated_data.pop('steps')

        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients_data:
            RecipeProduct.objects.create(recipe=recipe, **item)

        for step in steps_data:
            RecipeStep.objects.create(recipe=recipe, **step)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        steps_data = validated_data.pop('steps', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for item in ingredients_data:
                RecipeProduct.objects.create(recipe=instance, **item)

        if steps_data is not None:
            instance.steps.all().delete()
            for step in steps_data:
                RecipeStep.objects.create(recipe=instance, **step)

        return instance