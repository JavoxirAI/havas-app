from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.shared.models import BaseModel


class StoryType(models.TextChoices):
    """Story types similar to product categories"""
    PROMOTION = "PROMOTION", "Promotion"
    NEWS = "NEWS", "News"
    ANNOUNCEMENT = "ANNOUNCEMENT", "Announcement"
    FEATURED = "FEATURED", "Featured"
    ALL = "ALL", "All"


class StoryStatus(models.TextChoices):
    """Story status choices"""
    DRAFT = "DRAFT", "Draft"
    PUBLISHED = "PUBLISHED", "Published"
    ARCHIVED = "ARCHIVED", "Archived"


class Story(BaseModel):
    """
    Story model for displaying time-limited stories
    Similar to Instagram/WhatsApp stories
    """
    media_files = GenericRelation(
        'shared.Media',
        related_query_name='stories'
    )

    # Basic Information
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    # Story Type and Status
    story_type = models.CharField(
        max_length=20,
        choices=StoryType.choices,
        default=StoryType.ALL,
        db_index=True
    )
    status = models.CharField(
        max_length=10,
        choices=StoryStatus.choices,
        default=StoryStatus.DRAFT,
        db_index=True
    )

    # Display Settings
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )
    duration = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        help_text="Duration in seconds (1-30)"
    )

    # Timing
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Flags
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False)

    # Link/Action
    action_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="External link when story is clicked"
    )

    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'stories'
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'
        ordering = ['order', '-published_at']
        indexes = [
            models.Index(fields=['status', 'is_active'], name='story_status_active_idx'),
            models.Index(fields=['story_type', 'is_active'], name='story_type_active_idx'),
            models.Index(fields=['order', '-published_at'], name='story_order_pub_idx'),
            models.Index(fields=['expires_at'], name='story_expires_idx'),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_story_type_display()})"

    @property
    def is_expired(self):
        """Check if story has expired"""
        if not self.expires_at:
            return False

        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def is_published(self):
        """Check if story is published and active"""
        return (
                self.status == StoryStatus.PUBLISHED and
                self.is_active and
                not self.is_expired
        )

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_click_count(self):
        """Increment click count"""
        self.click_count += 1
        self.save(update_fields=['click_count'])

    @classmethod
    def get_active_stories(cls):
        """Get all active published stories that haven't expired"""
        from django.utils import timezone

        return cls.objects.filter(
            status=StoryStatus.PUBLISHED,
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        ).order_by('order', '-published_at')

    @classmethod
    def get_featured_stories(cls):
        """Get featured stories"""
        return cls.get_active_stories().filter(is_featured=True)


class StoryView(BaseModel):
    """
    Track story views by users/devices
    """
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='story_views'
    )
    device = models.ForeignKey(
        'users.Device',
        on_delete=models.CASCADE,
        related_name='story_views',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='story_views',
        null=True,
        blank=True
    )

    # View metadata
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    duration_watched = models.PositiveIntegerField(
        default=0,
        help_text="How many seconds user watched (in seconds)"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Whether user watched the entire story"
    )

    class Meta:
        db_table = 'story_views'
        verbose_name = 'Story View'
        verbose_name_plural = 'Story Views'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['story', '-viewed_at'], name='storyview_story_time_idx'),
            models.Index(fields=['device', '-viewed_at'], name='storyview_device_time_idx'),
            models.Index(fields=['user', '-viewed_at'], name='storyview_user_time_idx'),
        ]
        # Prevent duplicate views in short time
        unique_together = [['story', 'device', 'user']]

    def __str__(self):
        viewer = self.user.username if self.user else "Anonymous"
        return f"{viewer} viewed {self.story.title}"