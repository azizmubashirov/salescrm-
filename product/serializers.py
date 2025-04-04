from rest_framework import serializers
from .models import Type, Category, Product, Brand, Region, Color, ActiveProduct


class TypeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ('id', 'name')

class BrandSerializers(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    image = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = Brand
        fields = ('id', 'name', 'category', 'image', 'slug')
    
    def get_category(self, obj: Brand):
        try:
            category = Category.objects.filter(brand=obj)
            if category.exists():
                serializer = CategoryShortSerializers(category, many=True)
                return serializer.data
            return None
        except RecursionError as e:
            print(f"RecursionError: {e}")
            return None

class CategoryCreateSerializers(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = Category
        fields = ['id', 'name_uz', 'name_ru', 'parent', 'image', 'brand', 'is_home', 'is_popular', 'slug']
        
class CategorySerializers(serializers.ModelSerializer):
    brand = BrandSerializers()
    image = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = Category
        fields = ['id', 'name_uz', 'name_ru', 'parent', 'image', 'brand', 'is_home', 'is_popular', 'slug']
    
class ProductSerializers(serializers.ModelSerializer):
    # image = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'category', 'parent_category', 'image', 'description_uz', 'description_ru', 'is_popular')
        
class WebProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = ActiveProduct
        fields = ('id', 'product', 'status')
    
    def create(self, validated_data):
        product = ActiveProduct.objects.filter(product=validated_data['product']).first()
        if product:
            product.status = validated_data['status']
            product.save()    
            return product
        return super().create(validated_data)
        
        
class CategoryShortSerializers(serializers.ModelSerializer):
    # parent = CategorySerializers()
    class Meta:
        model = Category
        fields = ['id', 'name_uz', 'name_ru', 'slug', 'parent', 'image']
   

             
class ProductListSerializers(serializers.ModelSerializer):
    brand = BrandSerializers(read_only=True)
    category = CategoryShortSerializers(read_only=True)
    web_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'category', 'image', 'description_uz', 'description_ru', 'is_popular', 'web_active')

    def get_web_active(self, obj):
        active_product = ActiveProduct.objects.filter(product=obj).first()
        return active_product.status if active_product else False
    
class RegionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = [
            'id', 'name', 'created_at'
        ]

class ColorSerializers(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = [
            'id', 'name_uz', 'name_ru', 'created_at'
        ]

class DeleteSerializers(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of ids",
        max_length=100
    )

    def validate_ids(self, value):
        if not value:
            raise serializers.ValidationError("Id is not provided")
        return value