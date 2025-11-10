from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

from apps.stories.models import Story, StoryView, StoryStatus
from apps.stories.serializers.serializers import (
    StoryCreateSerializer,
    StoryListSerializer,
    StoryDetailSerializer
)
from apps.stories.permissions import IsAdminOrReadOnly
from apps.shared.utils.custom_response import CustomResponse


class StoryListCreateAPIView(ListCreateAPIView):
    """
    GET:  List all active stories (everyone)
    POST: Create a new story (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Return only active, non-expired stories"""
        queryset = Story.objects.filter(
            is_active=True,
            status=StoryStatus.ACTIVE
        ).prefetch_related('media_files')

        # Update expired stories
        now = timezone.now()
        expired_stories = queryset.filter(expires_at__lte=now)
        expired_stories.update(status=StoryStatus.EXPIRED, is_active=False)

        # Return only active stories
        return queryset.filter(expires_at__gt=now).order_by('order', '-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StoryCreateSerializer
        return StoryListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})

        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            request=request
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            story = serializer.save()
            response_serializer = StoryDetailSerializer(story, context={'request': request})

            return CustomResponse.success(
                message_key="STORY_CREATED_SUCCESSFULLY",
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED,
                request=request
            )

        return CustomResponse.error(
            message_key="VALIDATION_ERROR",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            request=request
        )


class StoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET:    Retrieve story details (everyone)
    PUT:    Update story (admin only)
    DELETE: Delete story (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Story.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StoryCreateSerializer
        return StoryDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Track view
        if request.user.is_authenticated:
            StoryView.objects.get_or_create(
                story=instance,
                user=request.user
            )
            instance.increment_view()

        serializer = self.get_serializer(instance, context={'request': request})

        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            request=request
        )