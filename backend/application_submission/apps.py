from django.apps import AppConfig


class ApplicationSubmissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'application_submission'
    verbose_name = '入職申請管理' # Admin界面顯示的應用名稱
