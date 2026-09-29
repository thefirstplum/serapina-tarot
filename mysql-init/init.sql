-- MySQL 초기화 스크립트
-- UTF-8 설정 및 기본 권한 부여

-- 데이터베이스 문자셋 설정
ALTER DATABASE tarot_chat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 추가 권한 부여 (필요한 경우)
GRANT ALL PRIVILEGES ON tarot_chat.* TO 'tarot_user'@'%';
FLUSH PRIVILEGES;

-- 기존 테이블이 있는 경우 IP 필드 제거 (개인정보 최소화)
-- 이 명령은 실패할 수 있지만 새로운 설치에서는 문제없습니다.
SET @sql = 'ALTER TABLE tarot_chat.tarot_sessions DROP COLUMN user_ip';
SET @sql_safe = CONCAT('SET @table_exists = (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = "tarot_chat" AND table_name = "tarot_sessions")');
PREPARE stmt FROM @sql_safe;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = 'SELECT COUNT(*) INTO @column_exists FROM information_schema.columns WHERE table_schema = "tarot_chat" AND table_name = "tarot_sessions" AND column_name = "user_ip"';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = IF(@column_exists > 0, 'ALTER TABLE tarot_chat.tarot_sessions DROP COLUMN user_ip', 'SELECT "user_ip column does not exist" as info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 기본 설정 확인용
SELECT 'MySQL for AI Tarot Chat is ready!' as status;