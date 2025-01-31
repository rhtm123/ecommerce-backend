from .models import Version
from .serializers import VersionSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class CustomPagination(PageNumberPagination):
    page_size = 15


class VersionListCreate(generics.ListCreateAPIView):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_fields = ("app_name",)
    search_fields = ("name","detail")
    ordering_fields = ("id", "created", "updated")
    pagination_class = CustomPagination


class VersionGetUpdate(generics.RetrieveUpdateAPIView):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class VersionGetUpdateSlug(generics.RetrieveUpdateAPIView):
    lookup_field = "slug"
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class VersionDelete(generics.DestroyAPIView):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)