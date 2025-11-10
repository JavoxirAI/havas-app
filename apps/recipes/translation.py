from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from apps.recipes.models import Recipe, RecipeStep


@register(Recipe)
class RecipeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(RecipeStep)
class RecipeStepTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'tips')