from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.products.models import Product


@receiver(pre_save, sender=Product)
def update_real_price_field(sender, instance, **kwargs):
    """
    Automatically calculate real_price based on discount

    Formula: real_price = price - (price * discount / 100)

    Examples:
    - price=1000, discount=10 -> real_price=900
    - price=1000, discount=0 -> real_price=1000
    """
    if instance.discount > 0:
        discount_amount = instance.price * instance.discount / 100
        instance.real_price = instance.price - discount_amount
    else:
        # Agar discount 0 bo'lsa, real_price = price
        instance.real_price = instance.price