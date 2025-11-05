from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.products.models import Product


@receiver(pre_save, sender=Product)
def update_real_price_field(sender, instance, **kwargs):
    if instance.discount > 0:
        instance.real_price = instance.price - (instance.price / 100 * instance.discount)
