from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from apps.stories.models import Story


@register(Story)
class StoryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
