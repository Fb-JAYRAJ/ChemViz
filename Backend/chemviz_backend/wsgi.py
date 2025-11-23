"""
WSGI config for chemviz_backend project.

This file exposes the WSGI callable used by web servers in production.
React (frontend) and the PyQt desktop app communicate only through this API.
"""

import os
from django.core.wsgi import get_wsgi_application

# Set settings module for WSGI environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chemviz_backend.settings")

# Create WSGI application instance
application = get_wsgi_application()