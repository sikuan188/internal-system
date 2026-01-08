from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # 移除 'username'，因為它將在 admin 的 save_model 中自動處理
        # 保留 'staff_id' 和其他您希望在創建表單中出現的字段
        fields = ('staff_id', 'email') # 根據您的實際需求調整，例如，如果 email 不是必填，可以移除