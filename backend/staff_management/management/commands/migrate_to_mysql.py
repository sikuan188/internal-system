import os
import json
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = '從SQLite遷移數據到MySQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            default='sqlite',
            help='源數據庫類型 (sqlite 或 mysql)',
        )
        parser.add_argument(
            '--target',
            default='mysql',
            help='目標數據庫類型 (sqlite 或 mysql)',
        )
        parser.add_argument(
            '--backup-file',
            default='sqlite_backup.json',
            help='備份文件名稱',
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        
        self.stdout.write(
            self.style.SUCCESS(f'🔄 開始數據庫遷移：{options["source"]} → {options["target"]}')
        )

        try:
            # 第一步：從SQLite導出數據
            if options['source'] == 'sqlite':
                self.stdout.write('📤 從SQLite導出數據...')
                # 設置環境變量使用SQLite
                os.environ['DB_ENGINE'] = 'sqlite'
                
                # 導出數據（排除敏感數據）
                call_command(
                    'dumpdata',
                    '--natural-foreign',
                    '--natural-primary',
                    '-e', 'contenttypes',
                    '-e', 'auth.Permission',
                    '--output', backup_file
                )
                self.stdout.write(self.style.SUCCESS(f'✅ 數據已導出到 {backup_file}'))

            # 第二步：切換到MySQL並導入數據
            if options['target'] == 'mysql':
                self.stdout.write('📥 切換到MySQL並導入數據...')
                # 設置環境變量使用MySQL
                os.environ['DB_ENGINE'] = 'mysql'
                
                # 重新加載設置（如果需要）
                from django.conf import settings
                settings._setup()
                
                # 運行遷移創建表結構
                call_command('migrate', '--run-syncdb')
                
                # 導入數據
                if os.path.exists(backup_file):
                    call_command('loaddata', backup_file)
                    self.stdout.write(self.style.SUCCESS('✅ 數據已導入到MySQL'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ 備份文件 {backup_file} 不存在'))
                    return

            # 第三步：驗證數據完整性
            self.stdout.write('🔍 驗證數據完整性...')
            from staff_management.models import StaffProfile
            from django.contrib.auth.models import User
            
            staff_count = StaffProfile.objects.count()
            user_count = User.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ 遷移完成！員工記錄: {staff_count}, 用戶記錄: {user_count}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 遷移失敗: {str(e)}')
            )
            raise