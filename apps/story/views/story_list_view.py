from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.story.models import Story, StoryStatus
from apps.story.serializers.serializers import (
    StoryCreateSerializer,
    StoryListSerializer,
    StoryPublicSerializer
)


class StoryListCreateAPIView(generics.ListCreateAPIView):
    """
    Story List and Create API View

    GET:
        - Public users: See only active, published stories (limited fields)
        - Admin users: See all stories with full details
        - Query parameters: story_type, status, is_featured, is_active

    POST:
        - Admin only: Create new story
        - Auto-sets published_at if status is PUBLISHED

    Examples:
        GET /api/v1/stories/
        GET /api/v1/stories/?story_type=PROMOTION
        GET /api/v1/stories/?status=PUBLISHED&is_featured=true
        POST /api/v1/stories/
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on request method and user type

        Returns:
            StoryCreateSerializer: For POST requests
            StoryListSerializer: For GET requests (admin users)
            StoryPublicSerializer: For GET requests (public users)
        """
        if self.request.method == 'POST':
            return StoryCreateSerializer

        # For GET requests
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return StoryListSerializer

        return StoryPublicSerializer

    def get_queryset(self):
        """
        Return appropriate queryset based on user type and filters

        Admin users:
            - See all stories
            - Can filter by story_type, status, is_featured, is_active

        Public users:
            - See only active, published, non-expired stories

        Returns:
            QuerySet: Filtered Story objects
        """
        queryset = Story.objects.all()

        # If user is admin/staff, show all stories with filters
        if self.request.user.is_authenticated and self.request.user.is_staff:
            # Apply query parameter filters
            story_type = self.request.query_params.get('story_type')
            status_filter = self.request.query_params.get('status')
            is_featured = self.request.query_params.get('is_featured')
            is_active = self.request.query_params.get('is_active')

            if story_type:
                queryset = queryset.filter(story_type=story_type)

            if status_filter:
                queryset = queryset.filter(status=status_filter)

            if is_featured is not None:
                is_featured_bool = is_featured.lower() == 'true'
                queryset = queryset.filter(is_featured=is_featured_bool)

            if is_active is not None:
                is_active_bool = is_active.lower() == 'true'
                queryset = queryset.filter(is_active=is_active_bool)

            return queryset.order_by('order', '-published_at')

        # For public users, only show active published stories
        return Story.get_active_stories()

    def perform_create(self, serializer):
        """
        Create story and auto-set published_at if status is PUBLISHED

        Args:
            serializer: Validated serializer instance
        """
        if serializer.validated_data.get('status') == StoryStatus.PUBLISHED:
            if not serializer.validated_data.get('published_at'):
                serializer.save(published_at=timezone.now())
            else:
                serializer.save()
        else:
            serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Create a new story with custom response format

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with success message and created data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'success': True,
                'message': 'Story created successfully',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def list(self, request, *args, **kwargs):
        """
        List stories with custom response format

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with stories list
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })