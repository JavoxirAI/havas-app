from django.db import models
from apps.products.models import Product

class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    rating = models.FloatField(default=0)
    calories = models.PositiveIntegerField(default=0)
    time_minutes = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RecipeProduct(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveIntegerField()
    text = models.TextField()

    class Meta:
        ordering = ['step_number']
        unique_together = ('recipe', 'step_number')

    def __str__(self):
        return f"Step {self.step_number} of {self.recipe.name}"
