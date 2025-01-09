from ecommerce.settings import *

import cloudinary


CORS_ALLOW_ALL_ORIGINS = True # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True


# CLOUDINARY_STORAGE = {
#     'CLOUD_NAME': config('CLN_CLOUD_NAME'),
#     'API_KEY': config('CLN_API_KEY'),
#     'API_SECRET': config('CLN_API_SECRET'),
# }

cloudinary.config(
    cloud_name=config('CLN_CLOUD_NAME'),
    api_key=config('CLN_CLOUD_NAME'),
    api_secret=config('CLN_CLOUD_NAME'),
    secure=True
)

import cloudinary.uploader
import cloudinary.api

# print(CLOUDINARY_STORAGE)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'