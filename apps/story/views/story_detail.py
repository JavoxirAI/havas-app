from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.story.models import Story
from apps.story.serializers.serializers import (
    StoryDetailSerializer,
    StoryUpdateSerializer,
    StoryPublicSerializer
)


class StoryDetailRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Story Detail, Update, and Delete API View

    GET:
        - Public users: See only active, published stories (limited fields)
        - Admin users: See full story details

    PUT/PATCH:
        - Admin only: Update story (full or partial)

    DELETE:
        - Admin only: Delete story

    Examples:
        GET    /api/v1/stories/1/
        PUT    /api/v1/stories/1/
        PATCH  /api/v1/stories/1/
        DELETE /api/v1/stories/1/
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def get_serializer_class(self):
        """
        Return appropriate serializer based on request method and user type

        Returns:
            StoryUpdateSerializer: For PUT/PATCH requests
            StoryDetailSerializer: For GET requests (admin users)
            StoryPublicSerializer: For GET requests (public users)
        """
        if self.request.method in ['PUT', 'PATCH']:
            return StoryUpdateSerializer

        # For GET requests
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return StoryDetailSerializer

        return StoryPublicSerializer

    def get_queryset(self):
        """
        Return appropriate queryset based on user type

        Admin users: See all stories
        Public users: See only active, published stories

        Returns:
            QuerySet: Story objects
        """
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Story.objects.all()

        # For public users, only show active published stories
        return Story.get_active_stories()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a story with custom response format

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with story data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            'success': True,
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        """
        Update a story with custom response format

        Supports both PUT (full update) and PATCH (partial update)

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with updated data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response({
            'success': True,
            'message': 'Story updated successfully',
            'data': serializer.data
        })

    def partial_update(self, request, *args, **kwargs):
        """
        Partial update (PATCH) with custom response

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with updated data
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a story with custom response format

        Args:
            request: HTTP request object

        Returns:
            Response: JSON response with success message
        """
        instance = self.get_object()
        story_title = instance.title
        self.perform_destroy(instance)

        return Response(
            {
                'success': True,
                'message': f'Story "{story_title}" deleted successfully'
            },
            status=status.HTTP_200_OK
        )