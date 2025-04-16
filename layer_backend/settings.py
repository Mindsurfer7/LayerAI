import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


# isDebugModeOn = (os.getenv("DEBUG_MODE"),)

# if
# isDebugModeOn and isDebugModeOn
# == False：
DEBUG = False
# else:
# DEBUG = True


# SECRET_KEY = "django-insecure-51_h2z=*+q*9iex5jz%q_^io4k*(z7@7&cdgvfdj=j5j%6*a&r"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-dev-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = [
    "178.88.34.26",
    "178.88.39.214",
    "193.93.122.13",
    "45.139.76.8",
    "178.88.39.214",
    # "localhost",
    # "10.0.2.2",
]

CHROME_EXT_KEY = os.getenv("CHROME_EXT_KEY")
CORS_ALLOWED_ORIGINS = ["chrome-extension://caahdpajgciilcgnckgjjbmfehnciefe"]
# CORS_ALLOWED_ORIGINS = ["chrome-extension://ffkebakejecfdiokegfddljmnamemhjp"]


# Application definition

INSTALLED_APPS = [
    "rest_framework.authtoken",
    "corsheaders",
    "djoser",
    "rest_framework",
    "users",
    "ai_chat",
    "memory",
    # "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "layer_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "layer_backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DEFAULT_CHARSET = 'utf-8'

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

DJOSER = {
    "USER_ID_FIELD": "id",
    "LOGIN_FIELD": "username",  # пока username, потом можно будет переключить на email
    "SERIALIZERS": {
        "user": "users.serializers.UserSerializer",  # сделаем позже
        "current_user": "users.serializers.UserSerializer",
    },
}

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["Authorization", "Content-Type"]
