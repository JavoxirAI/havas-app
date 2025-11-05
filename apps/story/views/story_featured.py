from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.story.models import Story
from apps.story.serializers.serializers import StoryPublicSerializer


class FeaturedStoriesListAPIView(generics.ListAPIView):
    """
    Featured Stories List API

    GET: Get all featured stories that are active and published

    Features:
        - Public access (no authentication required)
        - Only shows featured stories (is_featured=True)
        - Only shows active, published, non-expired stories
        - Ordered by order field and publication date
        - Limited fields for security (StoryPublicSerializer)

    Response includes:
        - id, uuid, title, description
        - story_type, duration, action_url
        - is_featured, order

    Examples:
        GET /api/v1/stories/featured/
    """
    serializer_class = StoryPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Return featured stories that are active and published

        Returns:
            QuerySet: Featured Story objects
        """
        return Story.get_featured_stories()

    def list(self, request, *args, **kwargs):
        """
        List featured stories with custom response format

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with featured stories
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
            'message': 'Featured stories retrieved successfully',
            'data': serializer.data
        })


class StoryByTypeListAPIView(generics.ListAPIView):
    """
    Stories By Type List API

    GET: Get stories filtered by story type

    URL Parameter:
        story_type: PROMOTION, NEWS, ANNOUNCEMENT, FEATURED, ALL

    Features:
        - Public access
        - Filter by story type
        - Only active, published stories

    Examples:
        GET /api/v1/stories/type/PROMOTION/
        GET /api/v1/stories/type/NEWS/
    """
    serializer_class = StoryPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Return stories filtered by type

        Returns:
            QuerySet: Filtered Story objects
        """
        story_type = self.kwargs.get('story_type')

        queryset = Story.get_active_stories()

        # Filter by story type if specified
        if story_type and story_type != 'ALL':
            queryset = queryset.filter(story_type=story_type)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        List stories by type with custom response format

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with stories
        """
        story_type = self.kwargs.get('story_type')
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'count': queryset.count(),
            'story_type': story_type,
            'message': f'{story_type} stories retrieved successfully',
            'data': serializer.data
        })


class ActiveStoriesListAPIView(generics.ListAPIView):
    """
    Active Stories List API

    GET: Get all active stories (published, not expired, active=true)

    Features:
        - Public access
        - Only shows active, published, non-expired stories
        - Includes all story types
        - Ordered by order and publication date

    Examples:
        GET /api/v1/stories/active/
    """
    serializer_class = StoryPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Return all active stories

        Returns:
            QuerySet: Active Story objects
        """
        return Story.get_active_stories()

    def list(self, request, *args, **kwargs):
        """
        List active stories with custom response format

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with active stories
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # Group stories by type for better organization
        stories_by_type = {}
        for story in queryset:
            story_type = story.story_type
            if story_type not in stories_by_type:
                stories_by_type[story_type] = []
            stories_by_type[story_type].append(story)

        type_counts = {
            story_type: len(stories)
            for story_type, stories in stories_by_type.items()
        }

        return Response({
            'success': True,
            'total_count': queryset.count(),
            'type_counts': type_counts,
            'message': 'Active stories retrieved successfully',
            'data': serializer.data
        })