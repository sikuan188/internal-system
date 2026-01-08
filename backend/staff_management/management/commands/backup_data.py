import os
import csv
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from staff_management.models import StaffProfile

class Command(BaseCommand):
    help = '備份員工數據和照片到本地桌面'

    def handle(self, *args, **options):
        # 備份路徑：可透過環境變數 BACKUP_PATH 覆寫，預設放桌面 /Users/kuan/Desktop/pcms_backup
        BACKUP_PATH = os.environ.get("BACKUP_PATH", "/Users/kuan/Desktop/pcms_backup")
        
        # 創建備份目錄
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(BACKUP_PATH, f"pcms_backup_{timestamp}")
        csv_dir = os.path.join(backup_dir, "csv_exports")
        photos_dir = os.path.join(backup_dir, "staff_photos")
        
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(photos_dir, exist_ok=True)
        
        self.stdout.write(f"開始備份到：{backup_dir}")
        
        # 1. 備份員工CSV數據
        csv_file_path = os.path.join(csv_dir, f"staff_data_backup_{timestamp}.csv")
        self.backup_staff_csv(csv_file_path)
        
        # 2. 備份員工照片
        photo_count = self.backup_staff_photos(photos_dir)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ 備份完成！\n"
                f"📁 備份位置：{backup_dir}\n"
                f"📄 CSV檔案：{os.path.basename(csv_file_path)}\n"
                f"📸 照片檔案：{photo_count} 個"
            )
        )

    def backup_staff_csv(self, csv_file_path):
        """備份員工數據為CSV格式"""
        try:
            staff_profiles = StaffProfile.objects.all().order_by('staff_id')
            
            with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # CSV標題行
                fieldnames = [
                    'staff_id', 'staff_name', 'employment_type', 'employment_type_remark',
                    'dsej_registration_status', 'dsej_registration_rank', 'entry_date',
                    'departure_date', 'retirement_date', 'position_grade',
                    'teaching_staff_salary_grade', 'basic_salary_points', 
                    'adjusted_salary_points', 'provident_fund_type', 'remark',
                    'contract_number', 'is_active', 'name_chinese', 'name_foreign',
                    'gender', 'marital_status', 'birth_place', 'birth_date', 'origin',
                    'id_type', 'id_number', 'id_expiry_date', 'bank_account_number',
                    'social_security_number', 'home_phone', 'mobile_phone', 'address',
                    'email', 'is_foreign_national', 'is_master', 'is_phd', 'is_overseas_study'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for staff in staff_profiles:
                    # 安全地獲取欄位值
                    def safe_get(obj, field_name, default=''):
                        try:
                            value = getattr(obj, field_name, default)
                            if value is None:
                                return default
                            return str(value)
                        except:
                            return default
                    
                    writer.writerow({
                        'staff_id': safe_get(staff, 'staff_id'),
                        'staff_name': safe_get(staff, 'staff_name'),
                        'employment_type': safe_get(staff, 'employment_type'),
                        'employment_type_remark': safe_get(staff, 'employment_type_remark'),
                        'dsej_registration_status': safe_get(staff, 'dsej_registration_status'),
                        'dsej_registration_rank': safe_get(staff, 'dsej_registration_rank'),
                        'entry_date': safe_get(staff, 'entry_date'),
                        'departure_date': safe_get(staff, 'departure_date'),
                        'retirement_date': safe_get(staff, 'retirement_date'),
                        'position_grade': safe_get(staff, 'position_grade'),
                        'teaching_staff_salary_grade': safe_get(staff, 'teaching_staff_salary_grade'),
                        'basic_salary_points': safe_get(staff, 'basic_salary_points'),
                        'adjusted_salary_points': safe_get(staff, 'adjusted_salary_points'),
                        'provident_fund_type': safe_get(staff, 'provident_fund_type'),
                        'remark': safe_get(staff, 'remark'),
                        'contract_number': safe_get(staff, 'contract_number'),
                        'is_active': safe_get(staff, 'is_active'),
                        'name_chinese': safe_get(staff, 'name_chinese'),
                        'name_foreign': safe_get(staff, 'name_foreign'),
                        'gender': safe_get(staff, 'gender'),
                        'marital_status': safe_get(staff, 'marital_status'),
                        'birth_place': safe_get(staff, 'birth_place'),
                        'birth_date': safe_get(staff, 'birth_date'),
                        'origin': safe_get(staff, 'origin'),
                        'id_type': safe_get(staff, 'id_type'),
                        'id_number': safe_get(staff, 'id_number'),
                        'id_expiry_date': safe_get(staff, 'id_expiry_date'),
                        'bank_account_number': safe_get(staff, 'bank_account_number'),
                        'social_security_number': safe_get(staff, 'social_security_number'),
                        'home_phone': safe_get(staff, 'home_phone'),
                        'mobile_phone': safe_get(staff, 'mobile_phone'),
                        'address': safe_get(staff, 'address'),
                        'email': safe_get(staff, 'email'),
                        'is_foreign_national': safe_get(staff, 'is_foreign_national'),
                        'is_master': safe_get(staff, 'is_master'),
                        'is_phd': safe_get(staff, 'is_phd'),
                        'is_overseas_study': safe_get(staff, 'is_overseas_study'),
                    })
            
            self.stdout.write(f"📄 CSV備份完成：{len(staff_profiles)} 筆員工資料")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ CSV備份失敗：{str(e)}")
            )

    def backup_staff_photos(self, photos_dir):
        """備份員工照片，重命名為員工編號格式"""
        photo_count = 0
        
        try:
            staff_profiles = StaffProfile.objects.exclude(profile_picture__isnull=True).exclude(profile_picture='')
            
            for staff in staff_profiles:
                if staff.profile_picture and staff.staff_id:
                    try:
                        # 取得原始照片路徑
                        source_path = staff.profile_picture.path
                        
                        if os.path.exists(source_path):
                            # 取得檔案副檔名
                            _, ext = os.path.splitext(source_path)
                            if not ext:
                                ext = '.jpg'  # 預設副檔名
                            
                            # 新檔案名稱：員工編號.jpg
                            new_filename = f"{staff.staff_id}{ext}"
                            destination_path = os.path.join(photos_dir, new_filename)
                            
                            # 複製並重命名照片
                            shutil.copy2(source_path, destination_path)
                            photo_count += 1
                            
                            self.stdout.write(f"📸 複製照片：{staff.staff_id} -> {new_filename}")
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️  照片複製失敗 {staff.staff_id}：{str(e)}")
                        )
            
            self.stdout.write(f"📸 照片備份完成：{photo_count} 個檔案")
            return photo_count
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ 照片備份失敗：{str(e)}")
            )
            return 0
