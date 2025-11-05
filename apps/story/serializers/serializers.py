from django.utils import timezone
from rest_framework import serializers

from apps.story.models import Story, StoryView, StoryStatus


class StoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating stories"""

    class Meta:
        model = Story
        fields = [
            'title', 'description', 'story_type', 'status',
            'order', 'duration', 'published_at', 'expires_at',
            'is_active', 'is_featured', 'action_url'
        ]

    def validate_duration(self, value):
        """Validate duration is between 1-30 seconds"""
        if value < 1 or value > 30:
            raise serializers.ValidationError(
                "Duration must be between 1 and 30 seconds"
            )
        return value

    def validate_expires_at(self, value):
        """Validate expiration date is in the future"""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiration date must be in the future"
            )
        return value

    def validate(self, attrs):
        """Validate published_at and expires_at relationship"""
        published_at = attrs.get('published_at')
        expires_at = attrs.get('expires_at')

        if published_at and expires_at:
            if expires_at <= published_at:
                raise serializers.ValidationError({
                    'expires_at': 'Expiration date must be after publication date'
                })

        return attrs

    def create(self, validated_data):
        """Auto-set published_at if status is PUBLISHED"""
        if validated_data.get('status') == StoryStatus.PUBLISHED:
            if not validated_data.get('published_at'):
                validated_data['published_at'] = timezone.now()

        return super().create(validated_data)


class StoryListSerializer(serializers.ModelSerializer):
    """Serializer for listing stories (admin view)"""
    is_expired = serializers.ReadOnlyField()
    is_published = serializers.ReadOnlyField()

    class Meta:
        model = Story
        fields = [
            'id', 'uuid', 'title', 'description', 'story_type',
            'status', 'order', 'duration', 'published_at', 'expires_at',
            'is_active', 'is_featured', 'action_url',
            'view_count', 'click_count', 'is_expired', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'view_count', 'click_count', 'created_at', 'updated_at']


class StoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for story detail (admin view)"""
    is_expired = serializers.ReadOnlyField()
    is_published = serializers.ReadOnlyField()
    story_type_display = serializers.CharField(source='get_story_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Story
        fields = [
            'id', 'uuid', 'title', 'description',
            'story_type', 'story_type_display',
            'status', 'status_display',
            'order', 'duration',
            'published_at', 'expires_at',
            'is_active', 'is_featured', 'action_url',
            'view_count', 'click_count',
            'is_expired', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'view_count', 'click_count', 'created_at', 'updated_at']


class StoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating stories"""

    class Meta:
        model = Story
        fields = [
            'title', 'description', 'story_type', 'status',
            'order', 'duration', 'published_at', 'expires_at',
            'is_active', 'is_featured', 'action_url'
        ]

    def validate_duration(self, value):
        """Validate duration is between 1-30 seconds"""
        if value < 1 or value > 30:
            raise serializers.ValidationError(
                "Duration must be between 1 and 30 seconds"
            )
        return value

    def validate_expires_at(self, value):
        """Validate expiration date"""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiration date must be in the future"
            )
        return value


class StoryPublicSerializer(serializers.ModelSerializer):
    """Serializer for public story view (limited fields)"""

    class Meta:
        model = Story
        fields = [
            'id', 'uuid', 'title', 'description',
            'story_type', 'duration', 'action_url',
            'is_featured', 'order'
        ]
        read_only_fields = ['id', 'uuid']


class StoryViewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating story views"""

    class Meta:
        model = StoryView
        fields = ['story', 'device', 'user', 'duration_watched', 'completed']

    def validate_story(self, value):
        """Validate story is active and published"""
        if not value.is_published:
            raise serializers.ValidationError(
                "Cannot view inactive or unpublished story"
            )
        return value