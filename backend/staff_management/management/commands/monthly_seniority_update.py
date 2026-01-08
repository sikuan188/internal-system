from django.core.management.base import BaseCommand
from staff_management.models import StaffProfile
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    每月自動更新所有員工年資的管理命令
    建議設置為cron job每月1日凌晨執行
    使用方法：python manage.py monthly_seniority_update
    """
    help = '每月自動更新所有員工的在校年資'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='預覽模式，不實際更新數據',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='強制執行，即使不是月初',
        )
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='只更新在職員工',
        )
    
    def handle(self, *args, **options):
        start_time = timezone.now()
        today = start_time.date()
        
        self.stdout.write(
            self.style.SUCCESS(f'=== 每月年資自動更新 {start_time.strftime("%Y-%m-%d %H:%M:%S")} ===')
        )
        
        # 檢查是否是月初（1-3日）或者強制執行
        if not options['force'] and today.day > 3:
            self.stdout.write(
                self.style.WARNING(f'今天是{today.day}日，不是月初。使用 --force 強制執行')
            )
            return
        
        # 篩選員工
        queryset = StaffProfile.objects.all()
        if options['active_only']:
            queryset = queryset.filter(is_active=True)
            self.stdout.write('篩選條件：只更新在職員工')
        
        total_count = queryset.count()
        updated_count = 0
        error_count = 0
        
        self.stdout.write(f'找到 {total_count} 名員工需要更新年資')
        
        # 更新年資
        for staff in queryset:
            try:
                old_seniority = staff.school_seniority_description
                
                if not options['dry_run']:
                    # 直接調用年資計算方法
                    staff.calculate_school_seniority()
                    # 重新從資料庫讀取
                    staff.refresh_from_db()
                
                new_seniority = staff.school_seniority_description
                
                if old_seniority != new_seniority:
                    updated_count += 1
                    status_msg = f'{staff.staff_id} ({staff.name_chinese or staff.staff_name}): {old_seniority} → {new_seniority}'
                    if options['dry_run']:
                        status_msg += ' [預覽模式]'
                    self.stdout.write(
                        self.style.WARNING(status_msg)
                    )
                else:
                    # 只在verbose模式下顯示無變化的員工
                    if options['verbosity'] >= 2:
                        self.stdout.write(f'{staff.staff_id}: 年資無變化 ({old_seniority})')
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'更新員工 {staff.staff_id} 年資時發生錯誤: {str(e)}')
                )
                logger.error(f'月度年資更新失敗 - ID: {staff.staff_id}, 錯誤: {e}', exc_info=True)
        
        # 輸出總結
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(
            self.style.SUCCESS(f'\\n=== 月度年資更新完成 ===')
        )
        self.stdout.write(f'執行時間：{duration:.2f} 秒')
        self.stdout.write(f'總處理數：{total_count}')
        self.stdout.write(f'成功更新：{updated_count}')
        self.stdout.write(f'錯誤數量：{error_count}')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('注意：這是預覽模式，數據並未實際更新')
            )
        
        # 記錄到系統日誌
        if not options['dry_run']:
            logger.info(f'月度年資更新完成 - 處理:{total_count}, 更新:{updated_count}, 錯誤:{error_count}')
        
        # 建議設置cron job
        if updated_count > 0 or options['verbosity'] >= 1:
            self.stdout.write('\\n=== Cron Job 設置建議 ===')
            self.stdout.write('在系統中添加以下cron job每月自動執行：')
            self.stdout.write('0 2 1 * * cd /path/to/your/project && python manage.py monthly_seniority_update --active-only')
            self.stdout.write('（每月1日凌晨2點執行，只更新在職員工）')