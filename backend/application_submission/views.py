
import logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import StaffApplication
from .serializers import StaffApplicationSerializer

# 獲取 logger 實例
logger = logging.getLogger('application_submission')

class StaffApplicationCreateView(generics.CreateAPIView):
    """
    API view for creating new staff applications.
    This endpoint is for public submission, so no authentication is required.
    包含完整的輸入驗證和錯誤處理機制
    """
    queryset = StaffApplication.objects.all()
    serializer_class = StaffApplicationSerializer
    permission_classes = [permissions.AllowAny] # 允許任何用戶訪問此接口進行提交

    def create(self, request, *args, **kwargs):
        # 日誌記錄點 1: 記錄接收到請求
        logger.info(f"StaffApplicationCreateView: 接收到新的員工申請請求，來源IP: {self.get_client_ip(request)}")
        
        # 數據預處理和清理
        cleaned_data = self.preprocess_data(request.data)
        
        serializer = self.get_serializer(data=cleaned_data)
        if serializer.is_valid():
            try:
                with transaction.atomic():  # 使用資料庫事務確保數據一致性
                    self.perform_create(serializer)
                    headers = self.get_success_headers(serializer.data)
                    response_data = {
                        "submission_id": serializer.instance.submission_id, 
                        "message": "申請提交成功，感謝您的申請！ Application submitted successfully, thank you!",
                        "status": "submitted"
                    }
                    # 日誌記錄點 2: 記錄成功創建
                    logger.info(f"StaffApplicationCreateView: 員工申請創建成功: ID {serializer.instance.submission_id}, 申請人: {serializer.instance.name_chinese}")
                    return Response(
                        response_data,
                        status=status.HTTP_201_CREATED,
                        headers=headers
                    )
            except Exception as e:
                # 日誌記錄點 3: 記錄創建時的內部錯誤
                logger.error(f"StaffApplicationCreateView: 創建員工申請時發生內部錯誤: {str(e)}", exc_info=True)
                return Response(
                    {
                        "error": "服務器內部錯誤，請稍後再試。 Internal server error, please try again later.",
                        "details": "數據處理過程中出現問題 Error occurred during data processing"
                    }, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # 日誌記錄點 4: 記錄數據驗證失敗
            logger.warning(f"StaffApplicationCreateView: 員工申請數據驗證失敗: {serializer.errors}")
            
            # 格式化錯誤訊息
            formatted_errors = self.format_validation_errors(serializer.errors)
            
            return Response({
                "error": "提交的數據不符合要求 Submitted data does not meet requirements",
                "validation_errors": formatted_errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        """獲取客戶端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def preprocess_data(self, data):
        """預處理提交的數據，清理和格式化"""
        cleaned_data = data.copy()
        
        # 清理字串欄位的前後空白
        string_fields = [
            'name_chinese', 'name_foreign', 'marital_status', 'birth_place', 'origin',
            'id_type', 'id_number', 'bank_account_number', 'social_security_number',
            'home_phone', 'mobile_phone', 'address', 'email', 'alumni_class',
            'alumni_class_year', 'alumni_class_duration', 'teacher_certificate_number',
            'teaching_staff_rank', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship'
        ]
        
        for field in string_fields:
            if field in cleaned_data and isinstance(cleaned_data[field], str):
                cleaned_data[field] = cleaned_data[field].strip()
        
        return cleaned_data

    def format_validation_errors(self, errors):
        """格式化驗證錯誤訊息，提供更友好的錯誤反饋"""
        formatted_errors = {}
        
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                formatted_errors[field] = error_list[0] if error_list else "數據驗證失敗 Validation failed"
            else:
                formatted_errors[field] = str(error_list)
        
        return formatted_errors

# 後續可以根據需求添加其他視圖，例如：
# - 管理員查看所有申請列表的視圖 (ListAPIView)
# - 管理員查看/更新/刪除單個申請的視圖 (RetrieveUpdateDestroyAPIView)
# - 管理員審批申請的動作視圖 (APIView with custom action)
