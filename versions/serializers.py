from rest_framework import fields, serializers

from .models import Version

class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'