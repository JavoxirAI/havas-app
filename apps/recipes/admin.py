# from django.contrib import admin
# from modeltranslation.admin import TranslationAdmin
# from apps.recipes.models import Recipe, RecipeProduct, RecipeStep
#
#
# class RecipeProductInline(admin.TabularInline):
#     model = RecipeProduct
#     extra = 1
#     fields = ['product', 'quantity', 'is_optional', 'order']
#     autocomplete_fields = ['product']
#
#
# class RecipeStepInline(admin.StackedInline):
#     model = RecipeStep
#     extra = 1
#     fields = ['step_number', 'title', 'description', 'duration_minutes', 'tips']
#
#
# @admin.register(Recipe)
# class RecipeAdmin(TranslationAdmin):
#     list_display = ['name', 'difficulty', 'time_minutes', 'calories', 'rating', 'view_count', 'is_active', 'created_at']
#     list_filter = ['difficulty', 'is_active', 'created_at']
#     search_fields = ['name', 'description']
#     list_editable = ['is_active']
#     inlines = [RecipeProductInline, RecipeStepInline]
#     readonly_fields = ['view_count', 'uuid', 'created_at', 'updated_at']
#
#     fieldsets = (
#         ('Basic Information', {
#             'fields': ('name', 'description', 'is_active')
#         }),
#         ('Details', {
#             'fields': ('difficulty', 'servings', 'time_minutes', 'calories', 'rating')
#         }),
#         ('Statistics', {
#             'fields': ('view_count', 'uuid', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#
# @admin.register(RecipeProduct)
# class RecipeProductAdmin(admin.ModelAdmin):
#     list_display = ['recipe', 'product', 'quantity', 'is_optional', 'order']
#     list_filter = ['is_optional', 'product']
#     search_fields = ['recipe__name', 'product__title']
#     autocomplete_fields = ['recipe', 'product']
#
#
# @admin.register(RecipeStep)
# class RecipeStepAdmin(TranslationAdmin):
#     list_display = ['recipe', 'step_number', 'title', 'duration_minutes', 'created_at']
#     list_filter = ['recipe', 'created_at']
#     search_fields = ['recipe__name', 'title', 'description']
#     ordering = ['recipe', 'step_number']
#     autocomplete_fields = ['recipe']