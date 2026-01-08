from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """只允許管理員用戶訪問"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsAdminOrReadOnly(permissions.BasePermission):
    """允許管理員執行所有操作，允許行政人員只讀訪問"""
    def has_permission(self, request, view):
        # 允許行政人員進行 GET, HEAD, OPTIONS 請求
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.groups.filter(name='administrative').exists())
        # 只允許管理員進行修改操作
        return bool(request.user and request.user.is_staff)