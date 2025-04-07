from ecommerce.settings import *

import cloudinary


CORS_ALLOW_ALL_ORIGINS = True # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://87b2-2409-40c2-400d-bec1-e423-97ec-80a-ce5b.ngrok-free.app']




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