from ecommerce.settings import *
import cloudinary


ALLOWED_HOSTS += [
    'kb.up.railway.app',
    'nm.thelearningsetu.com', 
    "emotional-cecily-codingchaska-5e686914.koyeb.app",
    "localhost"
]

CSRF_TRUSTED_ORIGINS = ['https://nm.thelearningsetu.com', "https://emotional-cecily-codingchaska-5e686914.koyeb.app"]

# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:5173',
# ]



CORS_ALLOW_ALL_ORIGINS = True

MIDDLEWARE += [ 'domains.middleware.CustomCORSValidationMiddleware']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
        'OPTIONS': {'sslmode': 'require'},
        }
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLN_CLOUD_NAME'),
    'API_KEY': config('CLN_API_KEY'),
    'API_SECRET': config('CLN_API_SECRET'),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

import cloudinary.uploader
import cloudinary.api

# print(CLOUDINARY_STORAGE)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'