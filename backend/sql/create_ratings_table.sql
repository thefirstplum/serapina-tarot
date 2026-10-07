SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 평점 피드백 전용 테이블 생성
CREATE TABLE IF NOT EXISTS user_ratings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  session_id VARCHAR(255),
  reading_id INT COMMENT '타로 리딩 ID',
  rating INT NOT NULL COMMENT '평점 1-5',
  categories JSON COMMENT '선택한 카테고리 배열',
  comment TEXT COMMENT '추가 코멘트 (선택)',
  contact VARCHAR(255) COMMENT '연락처 (선택)',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_session_id (session_id),
  INDEX idx_rating (rating),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 기존 user_feedback 테이블 데이터를 user_ratings로 마이그레이션
-- (rating이 있는 것만)
INSERT INTO user_ratings (session_id, reading_id, rating, categories, comment, contact, created_at)
SELECT
  session_id,
  reading_id,
  rating,
  NULL as categories,  -- 기존 데이터에는 categories가 feedback_text에 텍스트로 저장됨
  feedback_text as comment,
  NULL as contact,
  timestamp as created_at
FROM user_feedback
WHERE rating IS NOT NULL;
