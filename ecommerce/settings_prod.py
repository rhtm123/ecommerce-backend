from ecommerce.settings import *
import cloudinary

ALLOWED_HOSTS += [
    'kb.up.railway.app',
    'nm.thelearningsetu.com',
    "emotional-cecily-codingchaska-5e686914.koyeb.app",
    # "localhost",
]

CSRF_TRUSTED_ORIGINS = [
    "https://nm.thelearningsetu.com",
    "https://emotional-cecily-codingchaska-5e686914.koyeb.app",
    "https://www.naigaonmarket.com",
    "https://naigaonmarket.vercel.app",
    # "http://localhost:5173"
]

CORS_ALLOW_ALL_ORIGINS = False 
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://www.naigaonmarket.com",
    "https://naigaonmarket.vercel.app",
    # "http://localhost:5173",
]

# MIDDLEWARE += [ 'domains.middleware.CustomCORSValidationMiddleware']


import dj_database_url


DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,  # recommended for production
    )
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