from rest_framework import generics
from files.models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

class FilesCreateApiView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    queryset = Image.objects.all()
    serializer_class = ImageSerializers

    def create(self, request, *args, **kwargs):
        file_serializer = self.serializer_class(data=request.data)
        if file_serializer.is_valid():
            file_instance = file_serializer.save()
            return Response({'file': file_instance.file.url}, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
