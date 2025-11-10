from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from apps.products.models import Product


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = [
        'title', 'price', 'real_price', 'discount',
        'measurement_type', 'category', 'is_active', 'created_at'
    ]
    list_filter = ['category', 'measurement_type', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['price', 'discount', 'is_active']
    readonly_fields = ['uuid', 'real_price', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price', 'discount', 'real_price')
        }),
        ('Category & Measurement', {
            'fields': ('category', 'measurement_type')
        }),
        ('Metadata', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )