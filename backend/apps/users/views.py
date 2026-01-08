from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import logout
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, OnboardingApplicationSerializer
from .models import User, OnboardingApplication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .models import User, OnboardingApplication, EducationHistory # 新增導入 EducationHistory
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, OnboardingApplicationSerializer, UserDetailSerializer
from .serializers import CustomTokenObtainPairSerializer, OnboardingApplicationSerializer # 修改此行，加入 OnboardingApplicationSerializer
from .models import OnboardingApplication # 新增導入
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated # Ensure AllowAny and IsAuthenticated are imported

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

def profile_view(request):
    return HttpResponse("這是用戶個人資料頁面。")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

from .permissions import IsAdminUser, IsAdminOrReadOnly

from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    # lookup_field = 'id' # 或者 'pk', 默認就是 'pk'

class DashboardStatsView(APIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    # lookup_field = 'id' # 或者 'pk', 默認就是 'pk'


class OnboardingApplicationCreateView(generics.CreateAPIView):
    queryset = OnboardingApplication.objects.all()
    serializer_class = OnboardingApplicationSerializer
    permission_classes = [AllowAny]
