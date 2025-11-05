from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from apps.products.models import Product


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)
