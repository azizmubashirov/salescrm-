from rest_framework import serializers
from files.models import Image

class ImageSerializers(serializers.ModelSerializer):
    file = serializers.FileField()
    class Meta:
        model = Image
        fields = ('file', ) 