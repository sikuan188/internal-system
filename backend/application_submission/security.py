# 資料庫安全性工具和驗證器
from django.core.exceptions import ValidationError
from django.db import models
import re
import logging

logger = logging.getLogger(__name__)

class SQLSecurityMixin:
    """
    SQL安全性混入類，提供額外的安全驗證功能
    """
    
    # 定義允許的查詢參數白名單
    ALLOWED_QUERY_PARAMS = {
        'gender': {'type': str, 'choices': ['M', 'F']},
        'is_foreign_national': {'type': str, 'choices': ['true', 'false']},
        'is_phd': {'type': str, 'choices': ['true', 'false']},
        'is_master': {'type': str, 'choices': ['true', 'false']},
        'is_overseas_study': {'type': str, 'choices': ['true', 'false']},
        'is_active': {'type': str, 'choices': ['true', 'false']},
        'ordering': {'type': str, 'choices': [
            'name_chinese', '-name_chinese', 
            'entry_date', '-entry_date',
            'staff_id', '-staff_id'
        ]},
        'limit': {'type': int, 'min': 1, 'max': 1000},
        'offset': {'type': int, 'min': 0}
    }
    
    @classmethod
    def validate_query_params(cls, request):
        """
        驗證查詢參數的安全性和有效性
        """
        validated_params = {}
        
        for param_name, param_value in request.GET.items():
            if param_name not in cls.ALLOWED_QUERY_PARAMS:
                logger.warning(f"未授權的查詢參數: {param_name}")
                continue
                
            param_config = cls.ALLOWED_QUERY_PARAMS[param_name]
            
            try:
                # 類型驗證
                if param_config['type'] == int:
                    validated_value = int(param_value)
                    # 範圍驗證
                    if 'min' in param_config and validated_value < param_config['min']:
                        continue
                    if 'max' in param_config and validated_value > param_config['max']:
                        continue
                else:
                    validated_value = str(param_value).strip()
                
                # 選擇驗證
                if 'choices' in param_config:
                    if validated_value not in param_config['choices']:
                        logger.warning(f"無效的參數值: {param_name}={param_value}")
                        continue
                
                validated_params[param_name] = validated_value
                
            except ValueError:
                logger.warning(f"參數類型錯誤: {param_name}={param_value}")
                continue
        
        return validated_params
    
    @staticmethod
    def sanitize_input(value):
        """
        清理和消毒輸入值，防止惡意內容
        """
        if not isinstance(value, str):
            return value
        
        # 移除潛在的SQL注入字符
        dangerous_patterns = [
            r"(union\s+select)", r"(drop\s+table)", r"(delete\s+from)",
            r"(insert\s+into)", r"(update\s+set)", r"(exec\s*\()",
            r"(script\s*>)", r"(<\s*script)", r"(javascript\s*:)"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value.lower()):
                logger.error(f"檢測到潛在的安全威脅: {value}")
                raise ValidationError("輸入包含不安全的內容")
        
        return value.strip()

class SecureQuerysetMixin:
    """
    安全查詢集混入類，提供安全的篩選功能
    """
    
    def get_secure_queryset(self, request, base_queryset):
        """
        基於驗證的參數安全地篩選查詢集
        """
        validated_params = SQLSecurityMixin.validate_query_params(request)
        queryset = base_queryset
        
        # 性別篩選
        gender = validated_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # 布爾值篩選
        bool_filters = [
            'is_foreign_national', 'is_phd', 'is_master', 
            'is_overseas_study', 'is_active'
        ]
        
        for filter_name in bool_filters:
            filter_value = validated_params.get(filter_name)
            if filter_value == 'true':
                queryset = queryset.filter(**{filter_name: True})
            elif filter_value == 'false':
                queryset = queryset.filter(**{filter_name: False})
        
        # 排序
        ordering = validated_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        # 分頁
        limit = validated_params.get('limit')
        offset = validated_params.get('offset', 0)
        if limit:
            queryset = queryset[offset:offset + limit]
        elif offset:
            queryset = queryset[offset:]
        
        return queryset

class DatabaseIntegrityValidator:
    """
    資料庫完整性驗證器
    """
    
    @staticmethod
    def validate_staff_data_integrity(staff_data):
        """
        驗證員工數據的完整性和一致性
        """
        errors = []
        
        # 檢查必填欄位
        required_fields = ['name_chinese', 'name_foreign', 'birth_date', 'id_number']
        for field in required_fields:
            if not staff_data.get(field):
                errors.append(f"必填欄位缺失: {field}")
        
        # 檢查日期邏輯
        birth_date = staff_data.get('birth_date')
        id_expiry_date = staff_data.get('id_expiry_date')
        entry_date = staff_data.get('entry_date')
        
        if birth_date and id_expiry_date:
            if id_expiry_date <= birth_date:
                errors.append("證件有效期必須在出生日期之後")
        
        if birth_date and entry_date:
            if entry_date <= birth_date:
                errors.append("入職日期必須在出生日期之後")
        
        # 檢查數據格式
        if staff_data.get('mobile_phone'):
            mobile = staff_data['mobile_phone'].strip()
            if not re.match(r'^6\d{3}-?\d{4}$', mobile):
                errors.append("澳門手機號碼格式不正確")
        
        if staff_data.get('email'):
            email = staff_data['email'].strip()
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                errors.append("電郵格式不正確")
        
        return errors

class QueryLogMixin:
    """
    查詢日誌混入類，記錄數據庫查詢操作
    """
    
    @staticmethod
    def log_query_operation(user, operation, model_name, filters=None, count=None):
        """
        記錄查詢操作日誌
        """
        log_message = f"用戶 {user} 執行 {operation} 操作於 {model_name}"
        if filters:
            log_message += f"，篩選條件: {filters}"
        if count is not None:
            log_message += f"，結果數量: {count}"
        
        logger.info(log_message)