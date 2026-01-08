-- 培正中學員工管理系統 - MySQL 初始化腳本
-- 創建額外的管理員用戶和設置

-- 創建額外的管理員用戶（可選）
-- CREATE USER 'admin_kuan'@'%' IDENTIFIED BY 'admin_password';
-- GRANT ALL PRIVILEGES ON pcms_staff_db.* TO 'admin_kuan'@'%';

-- 設置字符集
ALTER DATABASE pcms_staff_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 刷新權限
FLUSH PRIVILEGES;

-- 記錄初始化完成
SELECT 'MySQL 初始化完成' as status;