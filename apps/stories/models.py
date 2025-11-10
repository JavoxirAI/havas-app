from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone
from apps.shared.models import BaseModel


class StoryStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    DRAFT = "DRAFT", "Draft"


class Story(BaseModel):
    """
    Instagram-style stories for the app
    """
    media_files = GenericRelation(
        'shared.Media',
        related_query_name='stories'
    )

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)

    # Story metadata
    view_count = models.PositiveIntegerField(default=0)
    duration = models.PositiveSmallIntegerField(
        default=5,
        help_text="Duration in seconds (default: 5)"
    )

    # Status and visibility
    status = models.CharField(
        max_length=10,
        choices=StoryStatus.choices,
        default=StoryStatus.DRAFT,
        db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)

    # Expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Story will expire after this time"
    )

    # Order
    order = models.PositiveIntegerField(default=0, db_index=True)

    # Creator
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_stories'
    )

    class Meta:
        db_table = 'stories'
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active'], name='story_status_active_idx'),
            models.Index(fields=['expires_at'], name='story_expires_idx'),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    @property
    def is_expired(self):
        """Check if stories has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def increment_view(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def check_and_update_status(self):
        """Check expiration and update status"""
        if self.is_expired and self.status == StoryStatus.ACTIVE:
            self.status = StoryStatus.EXPIRED
            self.is_active = False
            self.save(update_fields=['status', 'is_active'])


class StoryView(BaseModel):
    """
    Track which users viewed which stories
    """
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='story_views'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='viewed_stories'
    )
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'story_views'
        verbose_name = 'Story View'
        verbose_name_plural = 'Story Views'
        unique_together = ['story', 'user']
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.username} viewed {self.story.title}"