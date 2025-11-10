from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.stories.models import Story, StoryStatus


@receiver(pre_save, sender=Story)
def auto_set_published_at(sender, instance, **kwargs):
    """
    Automatically set published_at when stories status changes to PUBLISHED
    """
    if instance.status == StoryStatus.PUBLISHED and not instance.published_at:
        instance.published_at = timezone.now()


@receiver(pre_save, sender=Story)
def validate_expiration_date(sender, instance, **kwargs):
    """
    Ensure expiration date is after publication date
    """
    if instance.published_at and instance.expires_at:
        if instance.expires_at <= instance.published_at:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                "Expiration date must be after publication date"
            )