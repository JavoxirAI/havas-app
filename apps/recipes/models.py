from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from apps.products.models import Product
from apps.shared.models import BaseModel


class DifficultyLevel(models.TextChoices):
    EASY = "EASY", "Easy"
    MEDIUM = "MEDIUM", "Medium"
    HARD = "HARD", "Hard"


class Recipe(BaseModel):
    media_files = GenericRelation(
        'shared.Media',
        related_query_name='recipes'
    )

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    rating = models.FloatField(default=0)
    calories = models.PositiveIntegerField(default=0)
    time_minutes = models.PositiveIntegerField(default=0)
    difficulty = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.MEDIUM
    )
    servings = models.PositiveIntegerField(default=1, help_text="Number of servings")

    is_active = models.BooleanField(default=True, db_index=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'recipes'
        ordering = ['-created_at']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class RecipeProduct(BaseModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50, help_text="e.g., 500g, 2 cups, 3 pieces")
    is_optional = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'recipe_products'
        ordering = ['order', 'id']
        verbose_name = 'Recipe Ingredient'
        verbose_name_plural = 'Recipe Ingredients'

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"


class RecipeStep(BaseModel):
    media_files = GenericRelation(
        'shared.Media',
        related_query_name='recipe_steps'
    )

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Time for this step in minutes"
    )
    tips = models.TextField(blank=True, help_text="Cooking tips for this step")

    class Meta:
        db_table = 'recipe_steps'
        ordering = ['step_number']
        unique_together = ('recipe', 'step_number')
        verbose_name = 'Recipe Step'
        verbose_name_plural = 'Recipe Steps'

    def __str__(self):
        return f"Step {self.step_number}: {self.recipe.name}"