from django.core.management.base import BaseCommand
from staff_management.models import StaffProfile
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    自動更新所有員工的在校年資計算
    使用方法：python manage.py update_seniority
    """
    help = '自動更新所有員工的在校年資'
    
    def add_arguments(self, parser):
        # 添加選項參數
        parser.add_argument(
            '--staff-id',
            type=str,
            help='只更新指定員工編號的年資（可選）',
        )
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='只更新在職員工的年資',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='預覽模式，不實際更新數據',
        )
    
    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(f'=== 開始更新員工年資 {start_time.strftime("%Y-%m-%d %H:%M:%S")} ===')
        )
        
        # 根據參數篩選員工
        queryset = StaffProfile.objects.all()
        
        if options['staff_id']:
            queryset = queryset.filter(staff_id=options['staff_id'])
            self.stdout.write(f'篩選條件：員工編號 = {options["staff_id"]}')
        
        if options['active_only']:
            queryset = queryset.filter(is_active=True)
            self.stdout.write('篩選條件：只更新在職員工')
        
        total_count = queryset.count()
        updated_count = 0
        error_count = 0
        
        self.stdout.write(f'找到 {total_count} 名員工需要處理')
        
        # 逐一處理每個員工
        for staff in queryset:
            try:
                old_seniority = staff.school_seniority_description
                
                if not options['dry_run']:
                    # 實際更新年資
                    staff.calculate_school_seniority()
                    # 重新從數據庫讀取更新後的值
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
                    self.stdout.write(f'{staff.staff_id}: 年資無變化 ({old_seniority})')
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'更新員工 {staff.staff_id} 時發生錯誤: {str(e)}')
                )
                logger.error(f'更新員工年資失敗 - ID: {staff.staff_id}, 錯誤: {e}', exc_info=True)
        
        # 輸出總結
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n=== 年資更新完成 ===')
        )
        self.stdout.write(f'處理時間：{duration:.2f} 秒')
        self.stdout.write(f'總處理數：{total_count}')
        self.stdout.write(f'成功更新：{updated_count}')
        self.stdout.write(f'錯誤數量：{error_count}')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('注意：這是預覽模式，數據並未實際更新')
            )