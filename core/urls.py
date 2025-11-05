"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView

from apps.shared.utils.decorators import superuser_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.urls.v1'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# swagger and redoc settings
schema_view = SpectacularSwaggerView.as_view(url_name='schema')
redoc_view = SpectacularRedocView.as_view(url_name='schema')

urlpatterns += [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]

if settings.DEBUG:
    # Open docs for everyone in dev
    urlpatterns += [
        path("api/v1/docs/", schema_view, name="swagger-ui"),
        path("api/v1/redoc/", redoc_view, name="redoc"),
    ]
else:
    # Require superuser login in prod
    urlpatterns += [
        path("api/v1/docs/", superuser_required(schema_view), name="swagger-ui"),
        path("api/v1/redoc/", superuser_required(redoc_view), name="redoc"),
    ]
