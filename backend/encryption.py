# -*- coding: utf-8 -*-
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
from typing import Optional, Union

class DataEncryption:
    """Fernet(AES-128-CBC + HMAC) 기반 암호화. 리딩 기록의 개인정보 컬럼 저장용."""
    
    def __init__(self, password: Optional[str] = None):
        """
        암호화 클래스 초기화
        
        Args:
            password: 암호화 키 생성용 패스워드 (환경변수에서 가져올 수 있음)
        """
        self.password = password or os.getenv('ENCRYPTION_PASSWORD')
        if not self.password:
            raise RuntimeError("ENCRYPTION_PASSWORD 환경변수가 설정되지 않았습니다. 서버를 시작할 수 없습니다.")
        self.salt = b'seraphina_tarot_salt_2024'  # 실제 운영 시에는 랜덤 생성 권장
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """PBKDF2로 패스워드에서 키 생성"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        return key
    
    def encrypt_text(self, plain_text: str) -> str:
        """평문을 암호화해서 base64 문자열로 반환"""
        if not plain_text:
            return ""
            
        try:
            encrypted_data = self.cipher.encrypt(plain_text.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            print(f"암호화 오류: {e}")
            raise Exception(f"암호화 실패: {e}")
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """encrypt_text의 역"""
        if not encrypted_text:
            return ""
            
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            print(f"복호화 오류: {e}")
            raise Exception(f"복호화 실패: {e}")
    
    def encrypt_json(self, data: Union[dict, list]) -> str:
        """dict/list를 JSON 직렬화 후 암호화"""
        try:
            json_string = json.dumps(data, ensure_ascii=False)
            return self.encrypt_text(json_string)
        except Exception as e:
            print(f"❌ JSON 암호화 오류: {e}")
            raise Exception(f"JSON 암호화 실패: {e}")
    
    def decrypt_json(self, encrypted_json: str) -> Union[dict, list, str]:
        """복호화 후 JSON 파싱. 암호화 안 된 레거시 데이터면 그대로 파싱"""
        try:
            decrypted_string = self.decrypt_text(encrypted_json)
            return json.loads(decrypted_string)
        except Exception as e:
            print(f"⚠️ JSON 복호화 오류: {e}")
            # 암호화 이전에 저장된 평문 데이터일 수 있음
            try:
                return json.loads(encrypted_json)
            except Exception:
                print(f"❌ JSON 파싱도 실패 - 데이터 손상 가능: {e}")
                raise Exception(f"JSON 복호화 실패: {e}")
    
    def encrypt_sensitive_data(self, data: dict) -> dict:
        """민감 필드만 암호화"""
        sensitive_fields = [
            'question',        # 사용자 질문
            'ai_response',     # AI 응답
            'selected_cards',  # 선택된 카드 (JSON 문자열)
            'user_agent'      # 브라우저 정보
        ]
        
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                if field == 'selected_cards':
                    # JSON 문자열인 경우 JSON 암호화 사용
                    try:
                        cards_data = json.loads(encrypted_data[field])
                        encrypted_data[field] = self.encrypt_json(cards_data)
                    except:
                        encrypted_data[field] = self.encrypt_text(str(encrypted_data[field]))
                else:
                    encrypted_data[field] = self.encrypt_text(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_sensitive_data(self, data: dict) -> dict:
        """민감 필드만 복호화"""
        sensitive_fields = [
            'question',
            'ai_response', 
            'selected_cards',
            'user_agent'
        ]
        
        decrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                if field == 'selected_cards':
                    # JSON 데이터인 경우 JSON 복호화 사용
                    decrypted_cards = self.decrypt_json(decrypted_data[field])
                    if isinstance(decrypted_cards, (list, dict)):
                        decrypted_data[field] = json.dumps(decrypted_cards)
                    else:
                        decrypted_data[field] = decrypted_cards
                else:
                    decrypted_data[field] = self.decrypt_text(decrypted_data[field])
        
        return decrypted_data


encryption = DataEncryption()

def get_encryption() -> DataEncryption:
    return encryption