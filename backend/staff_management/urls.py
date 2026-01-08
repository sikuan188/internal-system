from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    StaffProfileViewSet, 
    StatisticsView, 
    ImportStaffDataView,
    BatchPhotoUploadView,
    ChangePasswordView
)

router = DefaultRouter()
router.register(r'staff/profiles', StaffProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 員工相關API
    path('staff/statistics/', StatisticsView.as_view(), name='statistics'),
    path('staff/import/', ImportStaffDataView.as_view(), name='import-staff-data'),
    path('staff/batch-photo-upload/', BatchPhotoUploadView.as_view(), name='batch-photo-upload'),
    # 身份驗證API
    path('auth/login/', obtain_auth_token, name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
]