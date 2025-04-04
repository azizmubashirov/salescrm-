
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from user.serializers import UserListSerializers
from rest_framework import serializers
from datetime import datetime


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserListSerializers(self.user).data
        return data
    

class UserTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.context['request'].user.is_authenticated:
            data['user'] = UserListSerializers(self.context['request'].user).data
        return data
    
class RefreshTokenInputSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    
class LogoutSerializer(serializers.Serializer):
    def validate(self, attrs):
        return attrs