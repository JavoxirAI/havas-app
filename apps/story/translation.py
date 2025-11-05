from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from apps.story.models import Story


@register(Story)
class StoryTranslationOptions(TranslationOptions):
    """Translation options for Story model"""
    fields = ('title', 'description')