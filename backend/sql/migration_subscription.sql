-- 세라피나 구독 시스템 마이그레이션
-- 실행: mysql -u root serapina < migration_subscription.sql

-- 1. User 테이블에 구독 필드 추가
ALTER TABLE users
  ADD COLUMN subscription_tier VARCHAR(20) DEFAULT NULL AFTER point_balance,
  ADD COLUMN subscription_expires_at DATETIME DEFAULT NULL AFTER subscription_tier,
  ADD COLUMN subscription_auto_renew BOOLEAN DEFAULT FALSE AFTER subscription_expires_at;

-- 2. 구독 상품 테이블
CREATE TABLE IF NOT EXISTS subscription_plans (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  price INT NOT NULL,
  original_price INT DEFAULT NULL,
  duration_days INT NOT NULL,
  description VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  sort_order INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_code (code),
  INDEX idx_active (is_active)
);

-- 3. 구독 결제 기록 테이블
CREATE TABLE IF NOT EXISTS subscription_payments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  plan_code VARCHAR(50) NOT NULL,
  order_id VARCHAR(100) NOT NULL UNIQUE,
  payment_key VARCHAR(200) DEFAULT NULL,
  amount INT NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  confirmed_at DATETIME DEFAULT NULL,
  INDEX idx_user_id (user_id),
  INDEX idx_order_id (order_id),
  INDEX idx_status (status)
);

-- 4. 보상형 광고 시청 기록 테이블
CREATE TABLE IF NOT EXISTS rewarded_ad_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id VARCHAR(255),
  user_id INT DEFAULT NULL,
  ad_date DATE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_session_date (session_id, ad_date),
  INDEX idx_user_id (user_id)
);

-- 5. 기본 구독 상품 데이터 삽입
INSERT INTO subscription_plans (code, name, price, original_price, duration_days, description, sort_order) VALUES
  ('monthly', '월간 구독', 4900, 9900, 30, '매월 자동 갱신', 1),
  ('yearly', '연간 구독', 39000, 58800, 365, '연간 결제 (월 3,250원)', 2);
