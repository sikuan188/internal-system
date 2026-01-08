from django.core.management.base import BaseCommand
from staff_management.models import StaffProfile
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    自動修復員工姓名顯示問題
    解決name_chinese為'/'、空字符串或None的情況
    使用方法：python manage.py fix_staff_names
    """
    help = '自動修復員工姓名顯示問題，解決N/A顯示'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--staff-id',
            type=str,
            help='只處理指定員工編號（可選）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='預覽模式，不實際更新數據',
        )
        parser.add_argument(
            '--show-all',
            action='store_true',
            help='顯示所有員工的姓名狀態，包括正常的',
        )
    
    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(f'=== 開始修復員工姓名 {start_time.strftime("%Y-%m-%d %H:%M:%S")} ===')
        )
        
        # 根據參數篩選員工
        queryset = StaffProfile.objects.all()
        
        if options['staff_id']:
            queryset = queryset.filter(staff_id=options['staff_id'])
            self.stdout.write(f'篩選條件：員工編號 = {options["staff_id"]}')
        
        total_count = queryset.count()
        fixed_count = 0
        issue_count = 0
        
        self.stdout.write(f'找到 {total_count} 名員工需要檢查')
        self.stdout.write('\\n=== 姓名問題分析 ===')
        
        for staff in queryset:
            has_issue = False
            fix_applied = False
            issues = []
            
            # 檢查各種姓名問題
            if not staff.name_chinese or staff.name_chinese.strip() == '' or staff.name_chinese.strip() == '/':
                has_issue = True
                issues.append('中文姓名為空或為"/"')
                
                # 嘗試從其他欄位修復
                if not options['dry_run']:
                    if staff.name_foreign and staff.name_foreign.strip() and staff.name_foreign.strip() != '/':
                        # 使用外文姓名
                        staff.name_chinese = staff.name_foreign.strip()
                        fix_applied = True
                        issues.append(f'→ 修復為外文姓名: {staff.name_foreign.strip()}')
                    elif staff.staff_name and staff.staff_name.strip() and staff.staff_name.strip() != '/':
                        # 使用staff_name
                        staff.name_chinese = staff.staff_name.strip()
                        fix_applied = True
                        issues.append(f'→ 修復為staff_name: {staff.staff_name.strip()}')
                    else:
                        issues.append('→ 無法自動修復：所有姓名欄位都有問題')
                else:
                    # 預覽模式：提示可能的修復方案
                    if staff.name_foreign and staff.name_foreign.strip() and staff.name_foreign.strip() != '/':
                        issues.append(f'→ 可用外文姓名修復: {staff.name_foreign.strip()}')
                    elif staff.staff_name and staff.staff_name.strip() and staff.staff_name.strip() != '/':
                        issues.append(f'→ 可用staff_name修復: {staff.staff_name.strip()}')
                    else:
                        issues.append('→ 無法自動修復：所有姓名欄位都有問題')
            
            # 檢查外文姓名問題
            if not staff.name_foreign or staff.name_foreign.strip() == '' or staff.name_foreign.strip() == '/':
                # 如果中文姓名正常，這不算嚴重問題，但仍要記錄
                if not has_issue:  # 只在中文姓名正常時記錄外文姓名問題
                    issues.append('外文姓名為空或為"/"（非關鍵問題）')
            
            # 輸出結果
            if has_issue or options['show_all']:
                issue_count += 1 if has_issue else 0
                
                status_color = self.style.ERROR if has_issue else self.style.SUCCESS
                status_prefix = '❌' if has_issue else '✅'
                
                self.stdout.write(
                    status_color(f'{status_prefix} {staff.staff_id} ({staff.staff_name}):')
                )
                self.stdout.write(f'   中文姓名: {repr(staff.name_chinese)}')
                self.stdout.write(f'   外文姓名: {repr(staff.name_foreign)}')
                self.stdout.write(f'   staff_name: {repr(staff.staff_name)}')
                
                for issue in issues:
                    if '→' in issue:
                        self.stdout.write(self.style.WARNING(f'   {issue}'))
                    else:
                        self.stdout.write(f'   問題: {issue}')
                
                if fix_applied:
                    staff.save(update_fields=['name_chinese'])
                    fixed_count += 1
                    self.stdout.write(self.style.SUCCESS('   ✓ 已修復並保存'))
                elif has_issue and options['dry_run']:
                    self.stdout.write(self.style.WARNING('   [預覽模式，未實際修復]'))
                
                self.stdout.write('')  # 空行分隔
        
        # 輸出總結
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(self.style.SUCCESS(f'=== 姓名修復完成 ==='))
        self.stdout.write(f'處理時間：{duration:.2f} 秒')
        self.stdout.write(f'總檢查數：{total_count}')
        self.stdout.write(f'發現問題：{issue_count}')
        self.stdout.write(f'成功修復：{fixed_count}')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('注意：這是預覽模式，數據並未實際更新')
            )
        
        # 提供使用建議
        self.stdout.write('\\n=== 使用建議 ===')
        self.stdout.write('1. 先運行 --dry-run 預覽修復結果')
        self.stdout.write('2. 對於無法自動修復的員工，需要手動在Django admin中更新')
        self.stdout.write('3. 建議定期運行此命令檢查新增員工的姓名問題')