-- 포인트 시스템 초기 데이터
-- 실행: docker exec -i tarot_mysql mysql -u tarot_user -ptarot_pass tarot_chat --default-character-set=utf8mb4 < backend/init_point_data.sql

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 포인트 상품
INSERT INTO point_products (code, name, points, price, bonus_points, description, is_popular, is_active, sort_order) VALUES
('starter_50', '스타터', 50, 1000, 0, '가볍게 시작하기', 0, 1, 1),
('basic_100', '기본', 100, 1900, 10, '가장 기본적인 패키지', 0, 1, 2),
('popular_300', '인기', 300, 4900, 50, '가장 많이 선택해요!', 1, 1, 3),
('premium_700', '프리미엄', 700, 9900, 150, '최고의 가성비', 0, 1, 4);

-- 기능별 포인트 비용
INSERT INTO point_costs (feature_code, name, cost, description, is_active) VALUES
('extra_reading', '추가 리딩', 20, '일일 3회 초과 타로 리딩', 1),
('premium_reading', '프리미엄 리딩', 30, '더 상세하고 깊은 AI 해석', 1),
('extra_question', '추가 질문', 10, '30턴 대화 제한 이후 계속 대화', 1),
('special_spread', '특별 스프레드', 50, '켈틱 크로스, 연애 스프레드 등', 1);
