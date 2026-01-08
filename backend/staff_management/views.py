from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from .models import StaffProfile
from .serializers import StaffProfileSerializer
import logging
import json
# Import function moved inline

logger = logging.getLogger(__name__)
import tempfile
import os
import csv

# CSV import function
def import_data(csv_file_path):
    """
    完整的CSV匯入函數，支援所有欄位A-EN
    Returns the number of imported records
    """
    from datetime import datetime
    from .models import StaffProfile, FamilyMember, EducationBackground, WorkExperience, ProfessionalQualification, AssociationPosition
    
    def parse_date(date_str):
        """解析日期字符串為date物件，支援多種格式包括中文格式"""
        if not date_str or date_str.strip() == '' or date_str.strip().lower() in ['/', 'n/a', 'na', '無', 'null', 'none']:
            return None
        try:
            date_str = date_str.strip()
            
            # 處理中文日期格式 2024年8月10日
            import re
            chinese_date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
            match = re.match(chinese_date_pattern, date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day)).date()
            
            # 嘗試標準日期格式
            for date_format in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y', '%Y年%m月%d日']:
                try:
                    return datetime.strptime(date_str, date_format).date()
                except ValueError:
                    continue
        except:
            pass
        return None
    
    def parse_decimal(value):
        """解析Decimal值，處理空值和非數值"""
        if not value or value.strip() == '' or value.strip().lower() in ['/', 'n/a', 'na', '無', 'null', 'none']:
            return None
        try:
            value = str(value).strip()
            # 移除非數值字符（除了小數點和負號）
            import re
            value = re.sub(r'[^\d\.-]', '', value)
            if value and value not in ['-', '.', '-.']:
                return float(value)
        except:
            pass
        return None
    
    def parse_boolean(value):
        """解析布爾值"""
        if not value or value.strip() == '' or value.strip().lower() in ['/', 'n/a', 'na', '無', 'null', 'none']:
            return False
        value = value.strip().lower()
        return value in ['true', '1', 'yes', 'y', '是', 'true', 'TRUE']
    
    def clean_string(value):
        """清理字符串，處理空值標記"""
        if not value:
            return ''
        value = str(value).strip()
        if value.lower() in ['/', 'n/a', 'na', '無', 'null', 'none', 'nil']:
            return ''
        return value
    
    try:
        imported_count = 0
        errors = []
        
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # 清理BOM污染的鍵名和值
                    clean_row = {}
                    for key, value in row.items():
                        # 移除BOM字符從鍵名
                        clean_key = key.replace('\ufeff', '') if key else ''
                        # 移除BOM字符從值
                        clean_value = value.replace('\ufeff', '') if isinstance(value, str) else value
                        clean_row[clean_key] = clean_value
                    
                    # 驗證必要欄位 - 使用清理後的數據
                    staff_id = clean_string(clean_row.get('staff_id', ''))
                    staff_name = clean_string(clean_row.get('staff_name', ''))
                    
                    # 添加調試日志
                    logger.info(f"第{row_num}行: staff_id='{staff_id}', staff_name='{staff_name}', 清理后鍵名: {list(clean_row.keys())[:5]}")
                    
                    if not staff_id or not staff_name:
                        errors.append(f"第{row_num}行: 缺少必要欄位（staff_id='{staff_id}' 或 staff_name='{staff_name}'）")
                        continue
                    
                    # 檢查是否已存在
                    if StaffProfile.objects.filter(staff_id=staff_id).exists():
                        errors.append(f"第{row_num}行: 員工編號'{staff_id}'已存在")
                        continue
                    
                    # 創建StaffProfile記錄，包含所有基本欄位
                    staff_profile = StaffProfile(
                        # 基本資訊
                        staff_id=staff_id,
                        staff_name=staff_name,
                        employment_type=clean_string(row.get('employment_type')),
                        employment_type_remark=clean_string(row.get('employment_type_remark')),
                        dsej_registration_status=clean_string(row.get('dsej_registration_status')),
                        dsej_registration_rank=clean_string(row.get('dsej_registration_rank')),
                        entry_date=parse_date(row.get('entry_date')),
                        departure_date=parse_date(row.get('departure_date')),
                        retirement_date=parse_date(row.get('retirement_date')),
                        position_grade=clean_string(row.get('position_grade')),
                        teaching_staff_salary_grade=clean_string(row.get('teaching_staff_salary_grade')),
                        basic_salary_points=parse_decimal(row.get('basic_salary_points')),
                        adjusted_salary_points=parse_decimal(row.get('adjusted_salary_points')),
                        provident_fund_type=clean_string(row.get('provident_fund_type')),
                        remark=clean_string(row.get('remark')),
                        contract_number=clean_string(row.get('contract_number')),
                        
                        # 個人資訊
                        name_chinese=clean_string(row.get('name_chinese')) or staff_name,
                        name_foreign=clean_string(row.get('name_foreign')),
                        gender=clean_string(row.get('gender')) or 'M',
                        marital_status=clean_string(row.get('marital_status')),
                        birth_place=clean_string(row.get('birth_place')),
                        birth_date=parse_date(row.get('birth_date')),
                        origin=clean_string(row.get('origin')),
                        id_type=clean_string(row.get('id_type')),
                        id_number=clean_string(row.get('id_number')),
                        id_expiry_date=parse_date(row.get('id_expiry_date')),
                        bank_account_number=clean_string(row.get('bank_account_number')),
                        social_security_number=clean_string(row.get('social_security_number')),
                        home_phone=clean_string(row.get('home_phone')),
                        mobile_phone=clean_string(row.get('mobile_phone')),
                        address=clean_string(row.get('address')),
                        email=clean_string(row.get('email')),
                        alumni_class=clean_string(row.get('alumni_class')),
                        alumni_class_year=clean_string(row.get('alumni_class_year')),
                        alumni_class_duration=clean_string(row.get('alumni_class_duration')),
                        teacher_certificate_number=clean_string(row.get('teacher_certificate_number')),
                        teaching_staff_rank=clean_string(row.get('teaching_staff_rank')),
                        teaching_staff_rank_effective_date=parse_date(row.get('teaching_staff_rank_effective_date')),
                        emergency_contact_name=clean_string(row.get('emergency_contact_name')),
                        emergency_contact_phone=clean_string(row.get('emergency_contact_phone')),
                        emergency_contact_relationship=clean_string(row.get('emergency_contact_relationship')),
                        
                        # 布爾值欄位
                        is_foreign_national=parse_boolean(row.get('is_foreign_national')),
                        is_master=parse_boolean(row.get('is_master')),
                        is_phd=parse_boolean(row.get('is_phd')),
                        is_overseas_study=parse_boolean(row.get('is_overseas_study')),
                        is_active=parse_boolean(row.get('is_active', 'True'))
                    )
                    
                    staff_profile.save()
                    
                    # 匯入家庭成員資訊（1-5）
                    for i in range(1, 6):
                        name = clean_string(row.get(f'family_member_{i}_name'))
                        if name:
                            age_str = clean_string(row.get(f'family_member_{i}_age', '0'))
                            try:
                                age = int(age_str) if age_str.isdigit() else 0
                            except:
                                age = 0
                            FamilyMember.objects.create(
                                staff=staff_profile,
                                name=name,
                                relationship=clean_string(row.get(f'family_member_{i}_relationship')),
                                birth_date=parse_date(row.get(f'family_member_{i}_birth_date')),
                                age=age,
                                education_level=clean_string(row.get(f'family_member_{i}_education_level')),
                                institution=clean_string(row.get(f'family_member_{i}_institution')),
                                alumni_class=clean_string(row.get(f'family_member_{i}_alumni_class'))
                            )
                    
                    # 匯入學歷資訊（1-4）
                    for i in range(1, 5):
                        school_name = clean_string(row.get(f'education_{i}_school_name'))
                        if school_name:
                            degree_name = clean_string(row.get(f'education_{i}_degree_name'))
                            education_level = clean_string(row.get(f'education_{i}_education_level'))
                            
                            # 判斷學位類型
                            is_phd_degree = False
                            is_master_degree = False
                            is_overseas = False
                            
                            # 檢查是否為博士學位
                            if degree_name and any(keyword in degree_name.lower() for keyword in ['phd', 'ph.d', 'doctor', '博士']):
                                is_phd_degree = True
                            elif education_level and any(keyword in education_level.lower() for keyword in ['phd', 'ph.d', 'doctor', '博士']):
                                is_phd_degree = True
                                
                            # 檢查是否為碩士學位
                            if degree_name and any(keyword in degree_name.lower() for keyword in ['master', '碩士', 'msc', 'm.sc', 'ma', 'm.a']):
                                is_master_degree = True
                            elif education_level and any(keyword in education_level.lower() for keyword in ['master', '碩士', 'msc', 'm.sc', 'ma', 'm.a']):
                                is_master_degree = True
                                
                            # 檢查是否為海外學習
                            # 只在CSV沒有明確設定時才自動判斷
                            csv_overseas_setting = parse_boolean(row.get('is_overseas_study'))
                            if csv_overseas_setting:
                                # CSV明確設定為True，使用CSV設定
                                is_overseas = True
                            elif school_name and not any('\u4e00' <= char <= '\u9fff' for char in school_name):
                                # CSV未明確設定且學校名稱為非中文，才自動判斷為海外
                                is_overseas = True
                            
                            EducationBackground.objects.create(
                                staff=staff_profile,
                                study_period=clean_string(row.get(f'education_{i}_study_period')),
                                school_name=school_name,
                                education_level=education_level,
                                degree_name=degree_name,
                                certificate_date=parse_date(row.get(f'education_{i}_certificate_date')),
                                is_phd=is_phd_degree,
                                is_master=is_master_degree,
                                is_overseas_study=is_overseas
                            )
                    
                    # 匯入工作經驗（1-4）
                    for i in range(1, 5):
                        organization = clean_string(row.get(f'work_experience_{i}_organization'))
                        if organization:
                            WorkExperience.objects.create(
                                staff=staff_profile,
                                employment_period=clean_string(row.get(f'work_experience_{i}_employment_period')),
                                organization=organization,
                                position=clean_string(row.get(f'work_experience_{i}_position')),
                                salary=clean_string(row.get(f'work_experience_{i}_salary'))
                            )
                    
                    # 匯入專業資格（1-4）
                    for i in range(1, 5):
                        qualification_name = clean_string(row.get(f'professional_qualification_{i}_name'))
                        issue_date = parse_date(row.get(f'professional_qualification_{i}_issue_date'))
                        if qualification_name and issue_date:  # 只有當專業資格名稱和頒授日期都有值時才創建
                            ProfessionalQualification.objects.create(
                                staff=staff_profile,
                                qualification_name=qualification_name,
                                issuing_organization=clean_string(row.get(f'professional_qualification_{i}_issuing_organization')),
                                issue_date=issue_date
                            )
                    
                    # 匯入社團職務（1-4）
                    for i in range(1, 5):
                        association_name = clean_string(row.get(f'association_{i}_name'))
                        if association_name:
                            AssociationPosition.objects.create(
                                staff=staff_profile,
                                association_name=association_name,
                                position=clean_string(row.get(f'association_{i}_position')),
                                start_year=clean_string(row.get(f'association_{i}_start_year')),
                                end_year=clean_string(row.get(f'association_{i}_end_year'))
                            )
                    
                    # 更新教育標記 - CSV設定優先於自動計算
                    csv_is_master = parse_boolean(row.get('is_master'))
                    csv_is_phd = parse_boolean(row.get('is_phd')) 
                    csv_is_overseas = parse_boolean(row.get('is_overseas_study'))
                    
                    # 檢查CSV是否有明確的FALSE設定
                    csv_master_false = row.get('is_master', '').strip().lower() == 'false'
                    csv_phd_false = row.get('is_phd', '').strip().lower() == 'false'
                    csv_overseas_false = row.get('is_overseas_study', '').strip().lower() == 'false'
                    
                    # 先根據教育記錄自動更新
                    staff_profile.update_global_education_flags()
                    
                    # CSV設定優先：True或False都要尊重
                    if csv_is_master or csv_master_false:
                        staff_profile.is_master = csv_is_master
                    if csv_is_phd or csv_phd_false:
                        staff_profile.is_phd = csv_is_phd
                    if csv_is_overseas or csv_overseas_false:
                        staff_profile.is_overseas_study = csv_is_overseas
                        
                    # 保存最終的標記
                    staff_profile.save(update_fields=['is_master', 'is_phd', 'is_overseas_study'])
                    
                    imported_count += 1
                    
                except Exception as row_error:
                    errors.append(f"第{row_num}行處理錯誤: {str(row_error)}")
                    continue
        
        # 返回詳細結果資訊
        if errors:
            logging.warning(f"CSV匯入完成，成功{imported_count}條，錯誤{len(errors)}條: {errors[:5]}")
        else:
            logging.info(f"CSV匯入成功: {imported_count}條記錄")
            
        return {
            'imported_count': imported_count,
            'errors': errors,
            'total_rows_processed': len(list(csv.DictReader(open(csv_file_path, 'r', encoding='utf-8-sig')))) if imported_count > 0 or errors else 0
        }
        
    except Exception as e:
        logging.error(f"Error in import_data: {e}")
        return {
            'imported_count': 0,
            'errors': [f"檔案處理錯誤: {str(e)}"],
            'total_rows_processed': 0
        }

class StatisticsView(View):
    def get(self, request, *args, **kwargs):
        # 這裡編寫獲取統計數據的邏輯
        total_staff = StaffProfile.objects.count()
        # 可以添加更多統計數據
        data = {
            'totalStaff': total_staff,
            # 'averageExperience': ..., 
        }
        return JsonResponse(data)

class StaffProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StaffProfileSerializer
    # 預設只顯示在職員工，避免離職員工資料在前端顯示
    queryset = StaffProfile.objects.filter(is_active=True).order_by('-user_account__date_joined')
    permission_classes = [permissions.IsAuthenticated] # Initially, only authenticated users
    
    def get_queryset(self):
        """
        允許通過查詢參數控制是否顯示離職員工
        例如: /api/staff/?include_inactive=true
        """
        queryset = StaffProfile.objects.filter(is_active=True).order_by('-user_account__date_joined')
        include_inactive = self.request.query_params.get('include_inactive', '').lower()
        
        # 只有管理員才能查看離職員工資料
        if include_inactive == 'true' and (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = StaffProfile.objects.all().order_by('-user_account__date_joined')
            
        return queryset
    
    def get_serializer_context(self):
        """
        確保序列化器能夠訪問request對象，用於構造正確的圖片URL
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # We will add custom permission logic later to differentiate between admin and staff roles.

# You might want to add other viewsets for related models if they need to be managed independently,
# but for now, they are handled via the nested StaffProfileSerializer.

# 獲取一個 logger 實例。通常使用 __name__ 來命名 logger，
# 這樣日誌輸出時可以知道日誌來自哪個模塊。
logger = logging.getLogger(__name__)

class MyExampleView(View):
    def get(self, request, *args, **kwargs):
        logger.info("這是一個 INFO 級別的日誌消息，來自 MyExampleView 的 GET 請求。")
        try:
            # 假設這裡有一些可能出錯的操作
            # result = 1 / 0 
            # logger.debug(f"請求參數: {request.GET}") # DEBUG 級別，用於詳細調試
            data = {"message": "Hello from MyExampleView!"}
            logger.info(f"成功處理請求，返回數據: {data}")
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"處理請求時發生錯誤: {e}", exc_info=True) # exc_info=True 會記錄異常堆棧信息
            return JsonResponse({"error": "處理請求時發生內部錯誤"}, status=500)

# 您也可以在其他函數或類方法中使用 logger
def some_utility_function():
    logger.warning("這是一個來自 some_utility_function 的 WARNING 級別日誌。")

frontend_logger = logging.getLogger('frontend_events')

@method_decorator(csrf_exempt, name='dispatch') # 如果您的前端請求沒有 CSRF token，需要這個
class FrontendLogView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            log_level = data.get('level', 'info').lower() # 前端可以指定日誌級別
            message = data.get('message', '')
            details = data.get('details', {})

            log_entry = f"[Frontend Log - {log_level.upper()}] {message}"
            if details:
                log_entry += f" | Details: {json.dumps(details)}"

            if log_level == 'error':
                frontend_logger.error(log_entry)
            elif log_level == 'warning':
                frontend_logger.warning(log_entry)
            elif log_level == 'debug':
                frontend_logger.debug(log_entry)
            else: # 默認為 info
                frontend_logger.info(log_entry)
                
            return JsonResponse({"status": "success", "message": "Log received"}, status=200)
        except json.JSONDecodeError:
            frontend_logger.error("[Frontend Log View] Invalid JSON received for logging.")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            # 記錄這個視圖本身的錯誤到常規的後端錯誤日誌
            error_logger = logging.getLogger(__name__) # 或者 'django'
            error_logger.error(f"Error in FrontendLogView: {e}", exc_info=True)
            return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)

@method_decorator(csrf_exempt, name='dispatch') # 暫時禁用 CSRF，生產環境應使用 token
class BatchPhotoUploadView(APIView):
    """
    批量上傳員工照片的API端點
    支援多種上傳方式：
    1. 多個文件直接上傳，手動指定員工編號
    2. ZIP文件上傳，按文件名自動匹配員工編號
    """
    
    def post(self, request, *args, **kwargs):
        logger.info(f"[DEBUG] BatchPhotoUploadView.post user={request.user}")
        
        # 檢查用戶權限
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({"status": "error", "message": "權限不足"}, status=403)
        
        upload_type = request.data.get('upload_type', 'manual')  # manual 或 zip
        
        try:
            if upload_type == 'zip':
                return self._handle_zip_upload(request)
            else:
                return self._handle_manual_upload(request)
        except Exception as e:
            logger.error(f"批量照片上傳錯誤: {e}", exc_info=True)
            return JsonResponse({"status": "error", "message": f"上傳過程中發生錯誤: {str(e)}"}, status=500)
    
    def _handle_zip_upload(self, request):
        """處理ZIP文件上傳並自動匹配員工"""
        import zipfile
        import io
        from PIL import Image
        
        zip_file = request.FILES.get('zip_file')
        if not zip_file:
            return JsonResponse({"status": "error", "message": "沒有提供ZIP文件"}, status=400)
        
        if not zip_file.name.lower().endswith('.zip'):
            return JsonResponse({"status": "error", "message": "文件必須是ZIP格式"}, status=400)
        
        success_count = 0
        error_list = []
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                # 跳過目錄和隱藏文件
                if file_name.endswith('/') or file_name.startswith('__MACOSX/') or file_name.startswith('.'):
                    continue
                
                # 檢查是否為圖片文件
                if not file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    error_list.append(f"跳過非圖片文件: {file_name}")
                    continue
                
                # 從文件名提取員工編號（假設格式為：員工編號.jpg）
                base_name = file_name.split('/')[-1]  # 獲取文件名部分
                staff_id = base_name.split('.')[0]  # 去掉副檔名
                
                try:
                    # 查找對應的員工
                    staff = StaffProfile.objects.get(staff_id=staff_id)
                    
                    # 讀取圖片內容
                    with zip_ref.open(file_name) as img_file:
                        img_content = img_file.read()
                        
                        # 驗證圖片格式
                        try:
                            img = Image.open(io.BytesIO(img_content))
                            img.verify()  # 驗證圖片完整性
                        except Exception as img_error:
                            error_list.append(f"無效的圖片文件 {file_name}: {str(img_error)}")
                            continue
                        
                        # 保存圖片到媒體目錄
                        from django.core.files.base import ContentFile
                        from django.core.files.storage import default_storage
                        
                        # 生成唯一文件名
                        file_extension = file_name.lower().split('.')[-1]
                        new_filename = f"staff_photos/{staff_id}.{file_extension}"
                        
                        # 如果已存在舊照片，先刪除
                        if staff.profile_picture:
                            try:
                                default_storage.delete(staff.profile_picture.path)
                            except:
                                pass  # 忽略刪除錯誤
                        
                        # 保存新照片
                        saved_path = default_storage.save(new_filename, ContentFile(img_content))
                        staff.profile_picture = saved_path
                        staff.save()
                        
                        success_count += 1
                        
                except StaffProfile.DoesNotExist:
                    error_list.append(f"找不到員工編號 {staff_id} (文件: {file_name})")
                except Exception as e:
                    error_list.append(f"處理 {file_name} 時發生錯誤: {str(e)}")
        
        return JsonResponse({
            "status": "success",
            "message": f"批量上傳完成",
            "success_count": success_count,
            "error_count": len(error_list),
            "errors": error_list[:10]  # 只返回前10個錯誤
        })
    
    def _handle_manual_upload(self, request):
        """處理手動上傳多個照片文件"""
        # 這個功能留待前端實現時再完善
        return JsonResponse({"status": "error", "message": "手動上傳功能尚未實現"}, status=400)

@method_decorator(csrf_exempt, name='dispatch') # 暫時禁用 CSRF，生產環境應使用 token
class ImportStaffDataView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"[DEBUG] ImportStaffDataView.post user={request.user}, is_authenticated={getattr(request.user, 'is_authenticated', None)}, is_staff={getattr(request.user, 'is_staff', None)}, auth={getattr(request, 'auth', None)}, headers={dict(request.headers)}")
        if not request.user.is_staff: # 或者更嚴格的權限檢查，例如 is_superuser
            return JsonResponse({"status": "error", "message": "權限不足"}, status=403)

        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({"status": "error", "message": "沒有提供文件"}, status=400)

        if not csv_file.name.endswith('.csv'):
            return JsonResponse({"status": "error", "message": "文件格式必須是 CSV"}, status=400)

        tmp_file_path = None # 初始化以備在 except 塊中使用
        try:
            # 使用 delete=False 確保文件在關閉後不會立即被刪除
            # 我們將在 import_data 調用後手動刪除它
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb+') as tmp_file:
                for chunk in csv_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
                # 文件在這裡仍然是打開的，或者剛剛關閉，但因為 delete=False，它應該還存在
            
            # 現在 tmp_file_path 指向已保存的臨時文件
            # 調用導入數據的函數
            result = import_data(tmp_file_path)
            
            if result['errors']:
                # 有錯誤的情況
                error_details = '\n'.join(result['errors'][:10])  # 只顯示前10個錯誤
                remaining_errors = len(result['errors']) - 10
                if remaining_errors > 0:
                    error_details += f'\n... 還有 {remaining_errors} 個錯誤 (... and {remaining_errors} more errors)'
                
                if result['imported_count'] > 0:
                    # 部分成功 Partial Success
                    return JsonResponse({
                        "status": "warning", 
                        "message": f"部分導入成功 Partial Import Success：成功 Success {result['imported_count']} 條 records，失敗 Failed {len(result['errors'])} 條 records",
                        "details": error_details,
                        "imported_count": result['imported_count'],
                        "error_count": len(result['errors'])
                    }, status=200)
                else:
                    # 完全失敗 Complete Failure
                    return JsonResponse({
                        "status": "error", 
                        "message": f"導入失敗 Import Failed：0條成功 0 successful，{len(result['errors'])}條失敗 {len(result['errors'])} failed",
                        "details": error_details,
                        "imported_count": 0,
                        "error_count": len(result['errors'])
                    }, status=400)
            else:
                # 完全成功 Complete Success
                return JsonResponse({
                    "status": "success", 
                    "message": f"成功導入 Successfully Imported {result['imported_count']} 條員工記錄 staff records",
                    "imported_count": result['imported_count'],
                    "error_count": 0
                }, status=201)

        except Exception as e:
            logger.error(f"導入員工數據時發生錯誤: {e}", exc_info=True)
            return JsonResponse({"status": "error", "message": f"導入過程中發生錯誤: {str(e)}"}, status=500)
        finally:
            # 無論成功或失敗，都嘗試刪除臨時文件
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.remove(tmp_file_path)
                    logger.info(f"臨時文件 {tmp_file_path} 已成功刪除。")
                except Exception as e_remove:
                    logger.error(f"刪除臨時文件 {tmp_file_path} 時發生錯誤: {e_remove}", exc_info=True)


class ChangePasswordView(APIView):
    """
    密碼修改 API 端點
    允許已驗證用戶修改密碼
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        處理密碼修改請求
        
        請求格式:
        {
            "old_password": "現有密碼",
            "new_password": "新密碼",
            "new_password_confirm": "確認新密碼"
        }
        """
        try:
            data = request.data
            user = request.user
            
            # 獲取請求參數
            old_password = data.get('old_password', '')
            new_password = data.get('new_password', '')
            new_password_confirm = data.get('new_password_confirm', '')
            
            # 參數驗證
            if not old_password:
                return Response({
                    'success': False,
                    'message': '請輸入現有密碼',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not new_password:
                return Response({
                    'success': False,
                    'message': '請輸入新密碼',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(new_password) < 6:
                return Response({
                    'success': False,
                    'message': '新密碼長度至少需要6個字符',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if new_password != new_password_confirm:
                return Response({
                    'success': False,
                    'message': '新密碼與確認密碼不匹配',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 驗證現有密碼
            if not user.check_password(old_password):
                return Response({
                    'success': False,
                    'message': '現有密碼錯誤',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 新密碼不能與舊密碼相同
            if old_password == new_password:
                return Response({
                    'success': False,
                    'message': '新密碼不能與現有密碼相同',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 修改密碼
            user.set_password(new_password)
            user.save()
            
            # 更新會話，避免用戶被登出
            update_session_auth_hash(request, user)
            
            logger.info(f"用戶 {user.username} 成功修改密碼")
            
            return Response({
                'success': True,
                'message': '密碼修改成功',
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"密碼修改失敗: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': f'密碼修改失敗: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 您也可以在其他函數或類方法中使用 logger
def some_utility_function():
    logger.warning("這是一個來自 some_utility_function 的 WARNING 級別日誌。")
    # ... 其他邏輯 ...
