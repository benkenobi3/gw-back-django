from rest_framework_simplejwt.views import TokenObtainPairView

from src.serializers import UserTokenObtainPairSerializer


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
