"""
URL configuration for repbackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from ninja_simple_jwt.auth.views.api import mobile_auth_router, web_auth_router

from ninja import NinjaAPI

from users.api import router as users_api
from locations.api import router as locations_api

from carts.api import router as carts_api
from orders.api import router as orders_api

from products.api import router as products_api

from qna.api import router as qna_api
from reviews.api import router as reviews_api

from blogs.api import router as blogs_api

from django.conf import settings
from django.conf.urls.static import static


from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI




# api = NinjaAPI()


api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)


# api.add_router("/auth/mobile/", mobile_auth_router)
# api.add_router("/auth/web/", web_auth_router)


api.add_router("user/", users_api, tags=["Users API"])
api.add_router("location/", locations_api, tags=["Locations API"])
api.add_router("product/", products_api, tags=['Products API'])

api.add_router("cart/", carts_api, tags=['Carts API'])
api.add_router("order/", orders_api, tags=['Orders API'])
api.add_router("qna/", qna_api, tags=['Questions and Answers API'])
api.add_router("reviews/", reviews_api, tags=['Reviews API'])
api.add_router("blogs/", blogs_api, tags=['blogs API'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)