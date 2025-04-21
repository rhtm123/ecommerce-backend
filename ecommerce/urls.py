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


from users.api import router as users_api
from locations.api import router as locations_api

from carts.api import router as carts_api
from orders.api import router as orders_api

from products.api import router as products_api

from qna.api import router as qna_api
from reviews.api import router as reviews_api

from blogs.api import router as blogs_api

from estores.api import router as estores_api

from payments.api import router as payments_api

from offers.api import router as offers_api

from django.conf import settings
from django.conf.urls.static import static


from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from django.urls import include


api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)



api.add_router("payment/", payments_api, tags=['Payments API'])

api.add_router("user/", users_api, tags=["Users API"])
api.add_router("location/", locations_api, tags=["Locations API"])
api.add_router("product/", products_api, tags=['Products API'])

api.add_router("cart/", carts_api, tags=['Carts API'])
api.add_router("order/", orders_api, tags=['Orders API'])
api.add_router("qna/", qna_api, tags=['Questions and Answers API'])
api.add_router("review/", reviews_api, tags=['Reviews API'])
api.add_router("blog/", blogs_api, tags=['blogs API'])
api.add_router("estore/", estores_api, tags=['Estores API'])

api.add_router("offer/", offers_api, tags=['Offers API'])




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('summernote/', include('django_summernote.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)