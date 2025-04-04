from rest_framework import serializers
from user.models import User, Role, Permission
from typing import List
from store.serializers import StoreListSerializers
    

class UserSerializers(serializers.ModelSerializer):
    photo = serializers.CharField(write_only=True, required=False, allow_blank=True)
    passport_file = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = User
        fields = [
            'id', 'firstname', 'lastname', 'surname', 'password', 'login', 'role', 'permission', 'photo', 'store', 'passport_seria_number', 'passport_file', 'joined_date', 'order_price_change'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        permissions_data = validated_data.pop('permission', [])
        user = User.objects.create_user(**validated_data)
        user.permission.set(permissions_data)
        
        return user

class UserUpdateSerializers(serializers.ModelSerializer):
    photo = serializers.CharField(write_only=True, required=False, allow_blank=True)
    passport_file = serializers.CharField(write_only=True, required=False, allow_blank=True)
    new_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = User
        fields = [
            'id', 'firstname', 'lastname', 'surname', 'login', 'role', 'permission', 'photo', 'store', 'passport_seria_number', 'passport_file', 'joined_date', 'order_price_change', 'new_password'
        ]
    
    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password', None)
        
        if new_password:
            instance.set_password(new_password)
        return super().update(instance, validated_data)

    

class UserDeleteSerializers(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of ids",
        max_length=100
    )

    def validate_ids(self, value):
        if not value:
            raise serializers.ValidationError("Id is not provided")
        return value

class RoleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'created_at') 
   
class PermissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'slug', 'created_at')
        
class PermissionShortSerializers(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('slug', )

class UserListSerializers(serializers.ModelSerializer):
    role = RoleSerializers(read_only=True)
    access_urls = serializers.SerializerMethodField()
    store = StoreListSerializers()
    
    class Meta:
        model = User
        fields = [
            'id', 'firstname', 'lastname', 'surname', 'login', 'role', 'access_urls', 'permission', 'photo', 'store', 'passport_seria_number', 'passport_file', 'joined_date', 'order_price_change'
        ]
    def get_access_urls(self, obj: User) -> List[str]:
        return list(obj.permission.values_list('slug', flat=True))
   

    
