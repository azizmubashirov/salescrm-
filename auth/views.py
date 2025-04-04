from .serializers import (UserTokenObtainPairSerializer, UserTokenRefreshSerializer, 
                          RefreshTokenInputSerializer, LogoutSerializer)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from datetime import datetime

class UserLoginView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

class TokenRefreshView(TokenRefreshView):
    serializer_class = UserTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
    
class LogoutView(APIView):
    serializer_class = LogoutSerializer
    @extend_schema(request=RefreshTokenInputSerializer)
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token or token has already been blacklisted."}, status=status.HTTP_400_BAD_REQUEST)