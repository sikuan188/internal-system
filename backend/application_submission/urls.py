from django.urls import path
from .views import StaffApplicationCreateView

app_name = 'application_submission' # 命名空間

urlpatterns = [
    path('submit/', StaffApplicationCreateView.as_view(), name='submit_application'),
    # 未來可以添加更多此應用的 URL 模式
]