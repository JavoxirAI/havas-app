from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from apps.stories.models import Story, StoryView, StoryStatus
from apps.shared.models import Media


class StoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating stories (Admin only)
    """
    title_uz = serializers.CharField(required=True, max_length=255)
    title_ru = serializers.CharField(required=False, allow_blank=True, max_length=255)
    title_en = serializers.CharField(required=False, allow_blank=True, max_length=255)

    description_uz = serializers.CharField(required=False, allow_blank=True)
    description_ru = serializers.CharField(required=False, allow_blank=True)
    description_en = serializers.CharField(required=False, allow_blank=True)

    media = serializers.ImageField(write_only=True, required=True)

    expires_in_hours = serializers.IntegerField(
        write_only=True,
        required=False,
        default=24,
        help_text="Story will expire after this many hours (default: 24)"
    )

    class Meta:
        model = Story
        fields = [
            'title_uz', 'title_ru', 'title_en',
            'description_uz', 'description_ru', 'description_en',
            'media', 'duration', 'status', 'order',
            'expires_in_hours'
        ]

    def create(self, validated_data):
        # Extract fields
        media = validated_data.pop('media')
        expires_in_hours = validated_data.pop('expires_in_hours', 24)

        title_uz = validated_data.pop('title_uz')
        title_ru = validated_data.pop('title_ru', '')
        title_en = validated_data.pop('title_en', '')

        description_uz = validated_data.pop('description_uz', '')
        description_ru = validated_data.pop('description_ru', '')
        description_en = validated_data.pop('description_en', '')

        # Set expiration time
        validated_data['expires_at'] = timezone.now() + timedelta(hours=expires_in_hours)

        # Get current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user

        # Create story
        story = Story.objects.create(**validated_data)

        # Set translations
        story.title_uz = title_uz
        story.title_ru = title_ru or title_uz
        story.title_en = title_en or title_uz

        story.description_uz = description_uz
        story.description_ru = description_ru or description_uz
        story.description_en = description_en or description_uz

        story.save()

        # Save media (TUZATILGAN)
        Media.objects.create(
            content_object=story,
            file=media,
            media_type='image',  # ← 'file_type' dan 'media_type' ga o'zgardi
            original_filename=media.name,  # ← Qo'shildi (required field)
            uploaded_by=request.user if request and request.user.is_authenticated else None  # ← Qo'shildi
        )

        return story


class StoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing stories
    """
    media_url = serializers.SerializerMethodField()
    is_viewed = serializers.SerializerMethodField()
    time_left = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            'id', 'uuid', 'title', 'description',
            'media_url', 'duration', 'view_count',
            'is_viewed', 'time_left', 'order',
            'created_at'
        ]

    def get_media_url(self, obj):
        request = self.context.get('request')
        media = obj.media_files.first()
        if media and request:
            return request.build_absolute_uri(media.file.url)
        elif media:
            return media.file.url
        return None

    def get_is_viewed(self, obj):
        """Check if current user has viewed this story"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return StoryView.objects.filter(
                story=obj,
                user=request.user
            ).exists()
        return False

    def get_time_left(self, obj):
        """Return seconds left until expiration"""
        if obj.expires_at:
            delta = obj.expires_at - timezone.now()
            return max(0, int(delta.total_seconds()))
        return None

    def to_representation(self, instance):
        """Return translated fields based on request language"""
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and hasattr(request, 'lang'):
            lang = request.lang.lower()
            title_field = f'title_{lang}'
            if hasattr(instance, title_field):
                data['title'] = getattr(instance, title_field) or instance.title_uz

            desc_field = f'description_{lang}'
            if hasattr(instance, desc_field):
                data['description'] = getattr(instance, desc_field) or instance.description_uz

        return data


class StoryDetailSerializer(StoryListSerializer):
    """
    Detailed story serializer with view tracking
    """

    class Meta(StoryListSerializer.Meta):
        fields = StoryListSerializer.Meta.fields + ['status', 'expires_at']