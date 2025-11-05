from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.shared.models import BaseModel


class MeasurementType(models.TextChoices):
    GR = "GR", "Gram"
    PC = "PC", "Peace"
    L = "L", "Litre"


class ProductCategory(models.TextChoices):
    BREAKFAST = "BREAKFAST", "Breakfast"
    LUNCH = "LUNCH", "Lunch"
    DINNER = "DINNER", "Dinner"
    ALL = "ALL", "All"


class Product(BaseModel):
    media_files = GenericRelation(
        'shared.Media',
        related_query_name='products'
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()

    discount = models.PositiveSmallIntegerField(default=0)
    price = models.DecimalField(max_digits=30, decimal_places=2)
    real_price = models.DecimalField(max_digits=30, decimal_places=2)

    category = models.CharField(
        choices=ProductCategory, default=ProductCategory.ALL,
        db_index=True
    )
    measurement_type = models.CharField(
        choices=MeasurementType, default=MeasurementType.GR
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
