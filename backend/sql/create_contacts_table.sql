SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 문의하기 전용 테이블 생성
CREATE TABLE IF NOT EXISTS user_contacts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  session_id VARCHAR(255),
  contact_type VARCHAR(50) NOT NULL COMMENT '문의 유형: 일반문의, 기능제안, 버그신고, 제휴문의',
  name VARCHAR(100) NOT NULL COMMENT '이름',
  email VARCHAR(255) NOT NULL COMMENT '이메일',
  message TEXT NOT NULL COMMENT '문의 내용',
  status VARCHAR(20) DEFAULT 'pending' COMMENT '처리 상태: pending, processing, resolved',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_session_id (session_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
