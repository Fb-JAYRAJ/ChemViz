"""
Main URL routing for the chemviz_backend project.

This file combines Django admin routes, DRF authentication routes,
and the API endpoints provided by the equipment app.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin site
    path('admin/', admin.site.urls),

    # DRF login/logout views (useful during development)
    path('api-auth/', include('rest_framework.urls')),

    # Equipment API endpoints
    path('api/', include('equipment.urls')),
]