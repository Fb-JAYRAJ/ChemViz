"""
Django settings for chemviz_backend project.

This file contains the core configuration for the Django backend,
including installed apps, middleware, database setup, and API behavior.
"""

from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Development secret key (not used in production deployments)
SECRET_KEY = "django-insecure-%!=d)f03qx5f&xx(y#7oglaj%2d!f5=8$w-yz-s%wi3$kd#2ot"

# Debug mode enabled for local development
DEBUG = True

# Allowing all hosts during development (simple setup for API + React)
ALLOWED_HOSTS = ["*"]


# -------------------------------------------------------------------
# INSTALLED APPLICATIONS
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party libraries
    "rest_framework",
    "corsheaders",

    # Local app containing API logic
    "equipment",
]


# -------------------------------------------------------------------
# MIDDLEWARE CONFIGURATION
# -------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # CORS support for the React + Desktop clients
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
# Allow all origins for local development usage
CORS_ALLOW_ALL_ORIGINS = True


# -------------------------------------------------------------------
# REST FRAMEWORK CONFIGURATION
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    # Basic + session authentication for API usage
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],

    # Require user authentication for all API routes
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


# Main URL configuration
ROOT_URLCONF = "chemviz_backend.urls"

# Template configuration (not heavily used in this project)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI entry point for production servers
WSGI_APPLICATION = "chemviz_backend.wsgi.application"


# -------------------------------------------------------------------
# DATABASE CONFIG (SQLite for simple local development)
# -------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# -------------------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# -------------------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# -------------------------------------------------------------------
# STATIC & MEDIA FILES
# -------------------------------------------------------------------
STATIC_URL = "static/"

MEDIA_URL = "/media/"
# Uploaded CSV files are stored inside /media/uploads/
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

import os
from django.contrib.auth.models import User

if not User.objects.filter(username="demo_user").exists():
    try:
        User.objects.create_user("demo_user", password="demo1234")
    except:
        pass