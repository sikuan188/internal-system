from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from staff_management.views import FrontendLogView

urlpatterns = [
    path('admin/', admin.site.urls), 
    # 員工管理相關API路由
    path('api/', include('staff_management.urls')),
    # 申請提交相關API路由  
    path('api/application/', include('application_submission.urls', namespace='application_submission_api')),
    # 身份驗證相關API路由
    path('api/auth/', include('rest_framework.urls')),
    path('api/api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # 前端日誌記錄
    path('api/log-frontend-event/', FrontendLogView.as_view(), name='log_frontend_event'),
]

# 開發環境下的媒體文件服務配置
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
