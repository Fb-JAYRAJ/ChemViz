"""
ASGI config for chemviz_backend project.

This file exposes the ASGI callable used for asynchronous web servers.
Most deployments still use WSGI, but ASGI provides support for async
features if needed in the future.
"""

import os
from django.core.asgi import get_asgi_application

# Set default settings module for ASGI environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chemviz_backend.settings")

# Create ASGI application instance
application = get_asgi_application()