from django.urls import path

from apps.story.views.story_detail import StoryDetailRetrieveUpdateDestroyAPIView
from apps.story.views.story_featured import FeaturedStoriesListAPIView, ActiveStoriesListAPIView, StoryByTypeListAPIView
from apps.story.views.story_list_view import StoryListCreateAPIView
from apps.story.views.story_view_create import StoryViewCreateAPIView, StoryViewListAPIView, StoryClickAPIView

app_name = 'story'

urlpatterns = [
    # Story CRUD
    path('', StoryListCreateAPIView.as_view(), name='list-create'),
    path('<int:pk>/', StoryDetailRetrieveUpdateDestroyAPIView.as_view(), name='detail'),

    # Featured and Filtered Stories
    path('featured/', FeaturedStoriesListAPIView.as_view(), name='featured'),
    path('active/', ActiveStoriesListAPIView.as_view(), name='active'),
    path('type/<str:story_type>/', StoryByTypeListAPIView.as_view(), name='by-type'),

    # Story View Tracking
    path('views/', StoryViewCreateAPIView.as_view(), name='view-create'),
    path('views/list/', StoryViewListAPIView.as_view(), name='view-list'),

    # Story Click Tracking
    path('<int:pk>/click/', StoryClickAPIView.as_view(), name='click'),
]