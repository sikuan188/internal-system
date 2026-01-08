# ==============================================
# Phase 4: 權限管理裝飾器和工具
# ==============================================
from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from .models import UserRole, SystemLog

def get_client_ip(request):
    """獲取客戶端真實IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_user_action(user, action, resource_type, resource_id=None, description="", request=None):
    """記錄用戶操作日誌"""
    try:
        log_data = {
            'user': user,
            'action': action,
            'resource_type': resource_type,
            'resource_id': str(resource_id) if resource_id else None,
            'description': description,
        }
        
        if request:
            log_data['ip_address'] = get_client_ip(request)
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        SystemLog.objects.create(**log_data)
    except Exception as e:
        print(f"日誌記錄失敗: {e}")

def get_user_role(user):
    """獲取用戶角色，如果沒有則返回None"""
    if not user.is_authenticated:
        return None
    try:
        return user.userrole
    except UserRole.DoesNotExist:
        return None

def require_permission(permission_name):
    """
    權限檢查裝飾器
    檢查用戶是否有指定權限
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': '需要登入'}, status=401)
            
            user_role = get_user_role(request.user)
            if not user_role or not user_role.is_active:
                return JsonResponse({'error': '用戶角色無效'}, status=403)
            
            # 檢查特定權限
            if not getattr(user_role, permission_name, False):
                log_user_action(
                    request.user, 'view', 'PermissionDenied', 
                    description=f"嘗試訪問需要 {permission_name} 權限的資源",
                    request=request
                )
                return JsonResponse({'error': f'權限不足，需要 {permission_name} 權限'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

class HasRolePermission(BasePermission):
    """
    DRF權限類別
    檢查用戶是否有指定的角色權限
    """
    
    def __init__(self, required_permission):
        self.required_permission = required_permission
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = get_user_role(request.user)
        if not user_role or not user_role.is_active:
            return False
            
        return getattr(user_role, self.required_permission, False)
    
    def has_object_permission(self, request, view, obj):
        # 對於特定對象的權限檢查
        user_role = get_user_role(request.user)
        if not user_role:
            return False
        
        # 一般員工只能查看自己的資料
        if user_role.role == 'staff' and hasattr(obj, 'user_account'):
            return obj.user_account == request.user
            
        return self.has_permission(request, view)

class CanViewAllStaff(HasRolePermission):
    """檢查是否可以查看所有員工資料"""
    def __init__(self):
        super().__init__('can_view_all_staff')

class CanEditStaffData(HasRolePermission):
    """檢查是否可以編輯員工資料"""
    def __init__(self):
        super().__init__('can_edit_staff_data')

class CanExportData(HasRolePermission):
    """檢查是否可以匯出資料"""
    def __init__(self):
        super().__init__('can_export_data')

class CanImportData(HasRolePermission):
    """檢查是否可以匯入資料"""
    def __init__(self):
        super().__init__('can_import_data')

class CanManageUsers(HasRolePermission):
    """檢查是否可以管理用戶"""
    def __init__(self):
        super().__init__('can_manage_users')

class CanViewStatistics(HasRolePermission):
    """檢查是否可以查看統計資料"""
    def __init__(self):
        super().__init__('can_view_statistics')

def is_admin_or_hr(user):
    """檢查用戶是否為管理員或HR"""
    user_role = get_user_role(user)
    return user_role and user_role.role in ['admin', 'hr']

def is_supervisor_or_above(user):
    """檢查用戶是否為主管或以上級別"""
    user_role = get_user_role(user)
    return user_role and user_role.role in ['admin', 'hr', 'supervisor']

def can_access_user_data(current_user, target_user):
    """檢查當前用戶是否可以訪問目標用戶的資料"""
    if current_user == target_user:
        return True  # 自己的資料
    
    return is_admin_or_hr(current_user)  # 管理員和HR可以看所有人的資料