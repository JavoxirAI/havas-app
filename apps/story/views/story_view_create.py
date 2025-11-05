from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.story.models import Story, StoryView
from apps.story.serializers.serializers import StoryViewCreateSerializer


class StoryViewCreateAPIView(generics.CreateAPIView):
    """
    Story View Tracking API

    POST: Record that a user/device viewed a story

    Features:
        - Automatically increments story view_count
        - Prevents duplicate views (unique_together constraint)
        - Works for both authenticated and anonymous users
        - Tracks viewing duration and completion status

    Request Body:
        {
            "story": 1,
            "device": 1,              # Optional
            "user": 1,                # Optional
            "duration_watched": 5,     # Optional (seconds)
            "completed": true          # Optional
        }

    Examples:
        POST /api/v1/stories/views/
        {
            "story": 1,
            "device": 1,
            "duration_watched": 5,
            "completed": true
        }
    """
    serializer_class = StoryViewCreateSerializer
    permission_classes = [AllowAny]
    queryset = StoryView.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create story view and increment story view count

        Handles:
            - New views: Creates record and increments counter
            - Duplicate views: Returns 200 OK (already recorded)
            - Invalid data: Returns 400 Bad Request

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with success/error message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Save the view
            view = serializer.save()

            # Increment story view count
            story = view.story
            story.increment_view_count()

            return Response(
                {
                    'success': True,
                    'message': 'Story view recorded successfully',
                    'data': {
                        'story_id': story.id,
                        'story_title': story.title,
                        'total_views': story.view_count,
                        'duration_watched': view.duration_watched,
                        'completed': view.completed
                    }
                },
                status=status.HTTP_201_CREATED
            )

        except IntegrityError:
            # View already exists (unique_together constraint)
            # This means the same user/device already viewed this story
            return Response(
                {
                    'success': True,
                    'message': 'Story view already recorded',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': 'Failed to record story view',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class StoryClickAPIView(generics.GenericAPIView):
    """
    Story Click Tracking API

    POST: Record that a user clicked on a story's action URL

    Features:
        - Increments story click_count
        - No authentication required
        - Simple click tracking without user/device data

    Examples:
        POST /api/v1/stories/1/click/
    """
    permission_classes = [AllowAny]

    def post(self, request, pk):
        """
        Increment story click count

        Args:
            request: HTTP request object
            pk: Story primary key

        Returns:
            Response: JSON response with success/error message
        """
        try:
            story = Story.objects.get(pk=pk)

            # Check if story is active and published
            if not story.is_published:
                return Response(
                    {
                        'success': False,
                        'message': 'Story is not available'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Increment click count
            story.increment_click_count()

            return Response(
                {
                    'success': True,
                    'message': 'Story click recorded successfully',
                    'data': {
                        'story_id': story.id,
                        'story_title': story.title,
                        'total_clicks': story.click_count,
                        'action_url': story.action_url
                    }
                },
                status=status.HTTP_200_OK
            )

        except Story.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Story not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': 'Failed to record story click',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class StoryViewListAPIView(generics.ListAPIView):
    """
    List Story Views (Admin only)

    GET: Get all views for a specific story

    Query Parameters:
        - story_id: Filter by story ID
        - completed: Filter by completion status (true/false)

    Examples:
        GET /api/v1/stories/views/list/?story_id=1
        GET /api/v1/stories/views/list/?completed=true
    """
    serializer_class = StoryViewCreateSerializer
    permission_classes = [AllowAny]  # Change to IsAdminUser in production

    def get_queryset(self):
        """
        Return filtered story views

        Returns:
            QuerySet: Filtered StoryView objects
        """
        queryset = StoryView.objects.all().select_related('story', 'user', 'device')

        # Filter by story ID
        story_id = self.request.query_params.get('story_id')
        if story_id:
            queryset = queryset.filter(story_id=story_id)

        # Filter by completion status
        completed = self.request.query_params.get('completed')
        if completed is not None:
            completed_bool = completed.lower() == 'true'
            queryset = queryset.filter(completed=completed_bool)

        return queryset.order_by('-viewed_at')

    def list(self, request, *args, **kwargs):
        """
        List story views with custom response format

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with views list
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # Calculate statistics
        total_views = queryset.count()
        completed_views = queryset.filter(completed=True).count()
        completion_rate = (completed_views / total_views * 100) if total_views > 0 else 0

        return Response({
            'success': True,
            'count': total_views,
            'statistics': {
                'total_views': total_views,
                'completed_views': completed_views,
                'completion_rate': round(completion_rate, 2)
            },
            'data': serializer.data
        })