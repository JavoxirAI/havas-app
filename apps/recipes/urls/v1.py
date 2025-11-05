from django.urls import path

from apps.recipes.views import RecipeListCreateAPIView, RecipeRetrieveUpdateDestroyAPIView

app_name = 'recipes'

urlpatterns = [
    path('', RecipeListCreateAPIView.as_view(), name='list-create'),
    path('<int:pk>/', RecipeRetrieveUpdateDestroyAPIView.as_view(), name='detail'),
]
