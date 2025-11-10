from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from apps.stories.models import Story, StoryView


@admin.register(Story)
class StoryAdmin(TranslationAdmin):
    list_display = ['title', 'status', 'view_count', 'order', 'expires_at', 'created_at']
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['order', '-created_at']
    readonly_fields = ['view_count', 'created_by']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'description')
        }),
        ('Media', {
            'fields': ('duration',)
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'order')
        }),
        ('Expiration', {
            'fields': ('expires_at',)
        }),
        ('Stats', {
            'fields': ('view_count', 'created_by')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ['story', 'user', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['story__title', 'user__username']
    readonly_fields = ['story', 'user', 'viewed_at']