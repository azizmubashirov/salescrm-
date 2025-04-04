from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import Response
from .models import Type, Category, Product, Brand, Region, Color, ActiveProduct
from .serializers import (TypeSerializers, CategorySerializers, ProductSerializers, 
                          ProductListSerializers, BrandSerializers, RegionSerializers,
                          ColorSerializers, DeleteSerializers, WebProductSerializers,
                          CategoryCreateSerializers)
from rest_framework.permissions import AllowAny


"""Product"""
class ProductListApiView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializers
    filterset_fields = ['brand', 'category']
    search_fields = ['name']
    permission_classes = [AllowAny]

class ProductCreateApiView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    permission_classes = [AllowAny]


class ProductUpdateApiView(generics.UpdateAPIView):
    serializer_class = ProductSerializers
    queryset = Product.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']
    permission_classes = [AllowAny]

class WebProductUpdateApiView(generics.CreateAPIView):
    serializer_class = WebProductSerializers
    queryset = ActiveProduct.objects.all()

class ProductDeleteApiView(generics.DestroyAPIView):
    serializer_class = DeleteSerializers
    queryset = Product.objects.all()
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Product.objects.filter(id__in=ids)
        queryset.delete()


        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    lookup_field = 'id'
    permission_classes = [AllowAny]


"""Type"""
class TypeListApiView(generics.ListAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializers
    search_fields = ['name']
    permission_classes = [AllowAny]

class TypeCreateApiView(generics.CreateAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializers


class TypeUpdateApiView(generics.UpdateAPIView):
    serializer_class = TypeSerializers
    queryset = Type.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']

class TypeDeleteApiView(generics.DestroyAPIView):
    serializer_class = DeleteSerializers
    queryset = Type.objects.all()

    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Type.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TypeDetailApiView(generics.RetrieveAPIView):
    serializer_class = TypeSerializers
    queryset = Type.objects.all()
    lookup_field = 'id'
    
    
"""Category"""
class CategoryListApiView(generics.ListAPIView):
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializers
    filterset_fields = ['parent', 'brand__slug']
    search_fields = ['name_uz', 'name_ru']
    permission_classes = [AllowAny]

class CategoryChildrenListApiView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializers
    search_fields = ['name_uz', 'name_ru']
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        parent = self.kwargs.get('parent', 0)
        parent_slug = self.kwargs.get('parent__slug', '')
        print(parent_slug)
        if parent:
            return self.queryset.filter(parent_id=parent)
        elif parent_slug:
            return self.queryset.filter(parent__slug=parent_slug)
        else:
            return self.queryset.filter(parent_id__isnull=False)

class CategoryCreateApiView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializers


class CategoryUpdateApiView(generics.UpdateAPIView):
    serializer_class = CategoryCreateSerializers
    queryset = Category.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']

class CategoryDeleteApiView(generics.DestroyAPIView):
    serializer_class = DeleteSerializers
    queryset = Category.objects.all()
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Category.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CategoryDetailApiView(generics.RetrieveAPIView):
    serializer_class = CategoryCreateSerializers
    queryset = Category.objects.all()
    lookup_field = 'id'
    
"""Brand"""

class BrandCreateApiView(generics.CreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializers


class BrandUpdateApiView(generics.UpdateAPIView):
    serializer_class = BrandSerializers
    queryset = Brand.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']

class BrandDeleteApiView(generics.DestroyAPIView):
    serializer_class = DeleteSerializers
    queryset = Brand.objects.all()
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Brand.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BrandDetailApiView(generics.RetrieveAPIView):
    serializer_class = BrandSerializers
    queryset = Brand.objects.all()
    lookup_field = 'id'

class BrandListApiView(generics.ListAPIView):
    serializer_class = BrandSerializers
    queryset = Brand.objects.all()
    search_fields = ['name']
    permission_classes = [AllowAny]
    
"""Region"""
class RegionCreateApiView(generics.CreateAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializers


class RegionUpdateApiView(generics.UpdateAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializers
    lookup_field = 'id'
    http_method_names = ['put']


class RegionListApiView(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializers
    search_fields = ['name']
    permission_classes = [AllowAny]


class RegionDeleteApiView(generics.DestroyAPIView):
    queryset = Region.objects.all()
    serializer_class = DeleteSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Region.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class RegionDetailApiView(generics.RetrieveAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializers
    lookup_field = 'id'
    
"""Color"""
class ColorCreateApiView(generics.CreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializers


class ColorUpdateApiView(generics.UpdateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializers
    lookup_field = 'id'
    http_method_names = ['put']


class ColorListApiView(generics.ListAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializers
    search_fields = ['name_uz', 'name_ru']
    permission_classes = [AllowAny]


class ColorDeleteApiView(generics.DestroyAPIView):
    queryset = Region.objects.all()
    serializer_class = DeleteSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Color.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ColorDetailApiView(generics.RetrieveAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializers
    lookup_field = 'id'