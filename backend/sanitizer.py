# -*- coding: utf-8 -*-
"""
민감한 개인정보 필터링 및 마스킹 유틸리티
"""
import re


class SensitiveDataSanitizer:
    """민감한 개인정보를 감지하고 마스킹하는 클래스"""

    def __init__(self):
        self.patterns = {
            # 주민등록번호: 6자리-7자리 또는 13자리
            'resident_number': [
                r'\b\d{6}[-\s]?\d{7}\b',
                r'\b\d{13}\b'
            ],
            # 계좌번호: 은행명 + 숫자 조합
            r'account_number': [
                r'(?:계좌|통장|입금|출금|이체)[\s]*(?:번호)?[\s]*[:：]?[\s]*\d[\d\-\s]{8,}',
                r'\b\d{3,4}[-\s]?\d{2,6}[-\s]?\d{2,8}\b'
            ],
            # 카드번호: 4자리씩 4개 또는 16자리
            'card_number': [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            ],
            # 전화번호: 010-1234-5678 형식
            'phone': [
                r'\b01[0-9][-\s]?\d{3,4}[-\s]?\d{4}\b',
                r'\b\d{2,3}[-\s]?\d{3,4}[-\s]?\d{4}\b'
            ],
            # 이메일 주소
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            # 주소 (도로명주소, 지번주소)
            'address': [
                r'(?:서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[\s]*(?:특별시|광역시|특별자치시|도|특별자치도)?[\s]*[가-힣\s]+(?:시|군|구)[\s]*[가-힣\s]+(?:동|읍|면|로|길)[\s]*\d+',
            ],
            # 여권번호
            'passport': [
                r'\b[A-Z]{1,2}\d{7,8}\b'
            ],
            # 운전면허번호
            'license': [
                r'\b\d{2}[-\s]?\d{2}[-\s]?\d{6}[-\s]?\d{2}\b'
            ],
        }

        # 경고 키워드
        self.sensitive_keywords = [
            '주민번호', '주민등록번호', '등록번호',
            '계좌번호', '통장번호', '카드번호', '신용카드',
            '비밀번호', '패스워드', 'password',
            '여권번호', '면허번호', '운전면허',
            '비밀', '개인정보', '민감정보'
        ]

    def contains_sensitive_data(self, text: str) -> bool:
        """텍스트에 민감한 정보가 포함되어 있는지 확인"""
        if not text:
            return False

        # 키워드 체크
        text_lower = text.lower()
        for keyword in self.sensitive_keywords:
            if keyword.lower() in text_lower:
                return True

        # 패턴 매칭
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return True

        return False

    def sanitize_text(self, text: str) -> tuple[str, bool]:
        """
        텍스트에서 민감한 정보를 마스킹

        Returns:
            (마스킹된 텍스트, 민감정보 발견 여부)
        """
        if not text:
            return text, False

        sanitized = text
        found_sensitive = False

        # 패턴별로 마스킹
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, sanitized)
                for match in matches:
                    found_sensitive = True
                    matched_text = match.group(0)
                    if category == 'email':
                        # 이메일은 앞부분만 일부 보여주기
                        masked = self._mask_email(matched_text)
                    elif category == 'phone':
                        # 전화번호는 중간 부분 마스킹
                        masked = self._mask_phone(matched_text)
                    else:
                        # 나머지는 전체 마스킹
                        masked = '[민감정보]'

                    sanitized = sanitized.replace(matched_text, masked)

        return sanitized, found_sensitive

    def _mask_email(self, email: str) -> str:
        """이메일 마스킹: abc***@domain.com"""
        try:
            local, domain = email.split('@')
            if len(local) <= 2:
                masked_local = '*' * len(local)
            else:
                masked_local = local[:2] + '*' * (len(local) - 2)
            return f"{masked_local}@{domain}"
        except:
            return '[이메일]'

    def _mask_phone(self, phone: str) -> str:
        """전화번호 마스킹: 010-****-5678"""
        # 숫자만 추출
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 10:
            return f"{digits[:3]}-****-{digits[-4:]}"
        return '[전화번호]'

    def should_block_save(self, text: str) -> tuple[bool, str]:
        """
        저장을 차단해야 하는지 확인

        Returns:
            (차단 여부, 경고 메시지)
        """
        if not text:
            return False, ""

        # 심각한 민감정보가 있는지 확인 (주민번호, 계좌번호, 카드번호)
        critical_patterns = {
            'resident_number': '주민등록번호',
            'account_number': '계좌번호',
            'card_number': '카드번호',
        }

        for category, label in critical_patterns.items():
            if category in self.patterns:
                for pattern in self.patterns[category]:
                    if re.search(pattern, text):
                        return True, f"⚠️ {label}가 포함되어 있어 저장할 수 없습니다. 민감한 정보는 입력하지 말아주세요."

        return False, ""


_sanitizer = None

def get_sanitizer() -> SensitiveDataSanitizer:
    """싱글톤 sanitizer 인스턴스 반환"""
    global _sanitizer
    if _sanitizer is None:
        _sanitizer = SensitiveDataSanitizer()
    return _sanitizer
