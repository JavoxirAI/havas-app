from django.urls import path, include

urlpatterns = [
    path('users/', include('apps.users.urls.v1', namespace='users')),
    path('products/', include('apps.products.urls.v1', namespace='products')),
    path('story/', include('apps.story.urls.v1', namespace='story')),
    path('recipes/', include('apps.recipes.urls.v1', namespace='recipes')),
    path('contact/', include('apps.contact.urls.v1', namespace='contact')),
]