"""
URL configuration for ${DJANGO_PROJECT_NAME} project.

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
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

admin.site.site_header = 'Sharma Academy Admin'
admin.site.site_title = 'Sharma Academy Admin Portal'
admin.site.index_title = 'Welcome to Sharma Academy'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users_management.urls')),

    # OpenAPI Schema (raw JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),

    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='swagger-ui'),

    # Redoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='redoc-ui'),
]

if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
