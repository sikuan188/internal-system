from django.urls import path
from . import views  # 添加这行导入views模块
from .views import RegisterView, LogoutView, OnboardingApplicationCreateView, UserListView, DashboardStatsView, UserDetailView # 修改这行，新增 UserDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CustomTokenObtainPairView

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'), # 新增登出URL
    path('onboarding/apply/', OnboardingApplicationCreateView.as_view(), name='onboarding_apply'), # 新增入職申請URL
    path('emp/list/', UserListView.as_view(), name='user_list'), # 新增獲取員工列表URL
    path('emp/<int:pk>/', UserDetailView.as_view(), name='user_detail'), # 新增員工詳細資料管理URL
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'), # 新增儀表板統計數據URL
]