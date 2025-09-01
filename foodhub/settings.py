# settings.py
from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env (local dev)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Security / Environment
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = os.getenv("DEBUG", "False") == "True"

if not DEBUG and SECRET_KEY == "dev-insecure-key-change-me":
    raise RuntimeError("SECRET_KEY env var is required in production.")

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,.herokuapp.com").split(",")
    if h.strip()
]

# CSRF trusted origins must include https://
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

if not DEBUG and not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        f"https://{host.lstrip('.')}"
        for host in ALLOWED_HOSTS
        if host not in ["localhost", "127.0.0.1"]
    ]

# Proxy / SSL settings for Heroku
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Secure cookies in production
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
SECURE_SSL_REDIRECT = not DEBUG

# -----------------------------
# Applications
# -----------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
    # Project apps
    "core",
    "users",
    "restaurants",
    "menu",
    "orders",
    "deliveries",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodhub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "orders.context_processors.cart_item_count",
                "core.context_processors.nav_flags",
            ],
        },
    },
]

WSGI_APPLICATION = "foodhub.wsgi.application"

# -----------------------------
# Database
# -----------------------------
DEFAULT_DB_URL = "sqlite:///" + str(BASE_DIR / "db.sqlite3")
DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL", DEFAULT_DB_URL),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# -----------------------------
# Authentication
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation." "CommonPasswordValidator"},
    {"NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator")},
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "login"

# -----------------------------
# I18N / TZ
# -----------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------
# Crispy Forms
# -----------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -----------------------------
# Static & Media
# -----------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------
# Cloudinary (media storage)
# -----------------------------
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL", "").strip()

if CLOUDINARY_URL:
    if not CLOUDINARY_URL.startswith("cloudinary://"):
        raise RuntimeError(
            "CLOUDINARY_URL must start with "
            "'cloudinary://API_KEY:API_SECRET@CLOUD_NAME'"
        )

    INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

    CLOUDINARY_STORAGE = {
        "CLOUDINARY_URL": CLOUDINARY_URL,
        "PREFIX": "foodhub",
    }
    os.environ.setdefault("CLOUDINARY_SECURE", "true")
