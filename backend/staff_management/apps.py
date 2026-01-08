from django.apps import AppConfig


class StaffManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff_management'
    verbose_name = '教職員管理' # Admin界面顯示的應用名稱
