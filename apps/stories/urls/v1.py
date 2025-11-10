from django.urls import path

from apps.stories.views.views import StoryDetailAPIView, StoryListCreateAPIView

app_name = 'stories'

urlpatterns = [
    path('', StoryListCreateAPIView.as_view(), name='list-create'),
    path('<int:pk>/', StoryDetailAPIView.as_view(), name='detail'),
]