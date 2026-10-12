from pathlib import Path
import os
from decouple import config
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files configuration
STATIC_URL = '/static/'  # URL prefix for serving static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directory where `collectstatic` collects files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'ehealth_hub/static'),  # Your app-specific static files
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',  # Ensures app-level static files are found
]

# Media files configuration
MEDIA_URL = '/media/'  # URL for serving media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Directory to store uploaded media files

# CKEditor configurations (if used)
CKEDITOR_UPLOAD_PATH = 'uploads/ckeditor/'  # Path where CKEditor stores uploaded files
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'  # Base path for CKEditor static files

# Security
SECRET_KEY = 'django-insecure-=+&e7cjhwuvi8j#kej$+s+#jdm@qsxhmy3n-%amqh-g-m+*^cd'
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = [
    ".vercel.app",
    "localhost",
    "127.0.0.1",
    "ehealth4cancer.org",
    "www.ehealth4cancer.org",
    "ehealth4cancer.eu",
    "www.ehealth4cancer.eu",
    "ehealthhub4cancer.github.io/ehealth_hub",
]
# Installed apps
INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',  # Ensures WhiteNoise doesn't interfere during development
    'rest_framework',  # For API support
    'corsheaders',  # For Cross-Origin Resource Sharing
     # (Optional) For custom Django admin interface
    'ckeditor',  # For CKEditor integration
    'cloudinary_storage',  # For media file storage
    'cloudinary',
    'ehealth_app',  # Your custom app
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Handles CORS headers
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'ehealth_hub/templates')],  # Custom templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Use a separate local SQLite database only when manage.py receives --test.
# Django's test runner creates its own temporary database from this configuration.
if os.environ.get('EHEALTH_TEST_MODE') == '1':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'ehealth_test.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

ROOT_URLCONF = 'ehealth_hub.urls'

# WhiteNoise settings for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Cross-Origin Resource Sharing (CORS)
CORS_ALLOW_HEADERS = [
    "content-type",
    "authorization",
    "x-csrftoken",
    "x-requested-with",
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://yourdomain.com",
    "https://ehealth4cancer.org",
    "https://www.ehealth4cancer.org",
    "https://ehealth4cancer.ie",
    "https://www.ehealth4cancer.ie",
    "http://www.ehealth4cancer.ie",
    "http://www.ehealth4cancer.org",
]

CORS_ALLOW_CREDENTIALS = True  # Allow cookies or credentials to be sent


# Cloudinary settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUD_NAME'),
    'API_KEY': config('API_KEY'),
    'API_SECRET': config('API_SECRET'),
}
DEFAULT_FILE_STORAGE = (
    'django.core.files.storage.FileSystemStorage'
    if os.environ.get('EHEALTH_TEST_MODE') == '1'
    else 'cloudinary_storage.storage.MediaCloudinaryStorage'
)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # put this to force next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                # put the name of your editor.ui.addButton here
                'Preview',
                'Maximize',

            ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
        # 'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}
# CORS settings
# CORS_ALLOW_ALL_ORIGINS = True
UNFOLD = {
    "SITE_TITLE": "eHealth Admin",
    "SITE_HEADER": "eHealth Hub",
    "SITE_SUBHEADER": "People and research",
    "SITE_SYMBOL": "health_and_safety",
    "SHOW_HISTORY": True,
    # Leave THEME unset so each user can choose light, dark, or system appearance.
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}
