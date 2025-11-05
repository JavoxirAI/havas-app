"""
Story Admin Configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin

from apps.story.models import Story, StoryView


@admin.register(Story)
class StoryAdmin(TranslationAdmin):
    """Admin configuration for Story model"""

    list_display = [
        'id', 'title', 'story_type', 'status_badge',
        'is_active', 'is_featured', 'order',
        'view_count', 'click_count', 'expiration_status',
        'created_at'
    ]

    list_filter = [
        'story_type', 'status', 'is_active',
        'is_featured', 'created_at'
    ]

    search_fields = ['title', 'description']

    readonly_fields = [
        'id', 'uuid', 'view_count', 'click_count',
        'is_expired', 'is_published', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'story_type', 'status')
        }),
        ('Display Settings', {
            'fields': ('order', 'duration', 'is_active', 'is_featured')
        }),
        ('Timing', {
            'fields': ('published_at', 'expires_at')
        }),
        ('Action', {
            'fields': ('action_url',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'click_count'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'uuid', 'is_expired', 'is_published', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['order', '-published_at']

    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'DRAFT': '#gray',
            'PUBLISHED': '#28a745',
            'ARCHIVED': '#6c757d'
        }
        color = colors.get(obj.status, '#gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def expiration_status(self, obj):
        """Display expiration status"""
        if obj.is_expired:
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        elif obj.expires_at:
            return format_html(
                '<span style="color: green;">Active</span>'
            )
        return format_html('<span style="color: gray;">No Expiry</span>')

    expiration_status.short_description = 'Expiration'

    actions = ['make_published', 'make_draft', 'make_featured', 'make_inactive']

    def make_published(self, request, queryset):
        """Bulk action to publish stories"""
        from django.utils import timezone
        updated = queryset.update(
            status='PUBLISHED',
            is_active=True,
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} stories published successfully.')

    make_published.short_description = 'Publish selected stories'

    def make_draft(self, request, queryset):
        """Bulk action to make stories draft"""
        updated = queryset.update(status='DRAFT')
        self.message_user(request, f'{updated} stories set to draft.')

    make_draft.short_description = 'Set selected stories to draft'

    def make_featured(self, request, queryset):
        """Bulk action to make stories featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} stories marked as featured.')

    make_featured.short_description = 'Mark selected stories as featured'

    def make_inactive(self, request, queryset):
        """Bulk action to make stories inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} stories deactivated.')

    make_inactive.short_description = 'Deactivate selected stories'


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    """Admin configuration for StoryView model"""

    list_display = [
        'id', 'story', 'user', 'device',
        'duration_watched', 'completed', 'viewed_at'
    ]

    list_filter = ['completed', 'viewed_at']

    search_fields = ['story__title', 'user__username', 'device__device_id']

    readonly_fields = ['id', 'story', 'device', 'user', 'viewed_at']

    fieldsets = (
        ('View Information', {
            'fields': ('story', 'user', 'device')
        }),
        ('View Metadata', {
            'fields': ('duration_watched', 'completed', 'viewed_at')
        })
    )

    list_per_page = 50
    date_hierarchy = 'viewed_at'
    ordering = ['-viewed_at']

    def has_add_permission(self, request):
        """Disable manual creation of story views"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of story views"""
        return False