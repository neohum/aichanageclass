# 보안 가이드

## 🔐 개인정보 보호 및 보안 정책

### 1. 데이터 보호 원칙

#### 1.1 로컬 우선 (Local-First)
- **모든 데이터는 사용자의 컴퓨터에만 저장**
- 외부 서버로 데이터 전송 없음
- 인터넷 연결 불필요
- 사용자가 데이터를 완전히 통제

#### 1.2 암호화 기본 (Encryption by Default)
- 데이터베이스 전체 암호화 (SQLCipher)
- 백업 파일 자동 암호화
- 민감 정보 메모리 보호
- 안전한 키 관리

#### 1.3 최소 권한 (Least Privilege)
- 필요한 권한만 요청
- 파일 시스템 접근 제한
- 사용자 승인 필수

### 2. 암호화 구현

#### 2.1 데이터베이스 암호화 (SQLCipher)

```python
# backend/security/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

def create_encrypted_engine(db_path: str, password: str):
    """암호화된 SQLite 데이터베이스 엔진 생성"""
    engine = create_engine(
        f'sqlite:///{db_path}',
        connect_args={
            'check_same_thread': False,
        },
        poolclass=StaticPool,
    )
    
    # SQLCipher 설정
    with engine.connect() as conn:
        # 암호화 키 설정
        conn.execute(f"PRAGMA key = '{password}'")
        # 암호화 알고리즘: AES-256
        conn.execute("PRAGMA cipher = 'aes-256-cbc'")
        # 키 파생 반복 횟수
        conn.execute("PRAGMA kdf_iter = 100000")
        # 페이지 크기
        conn.execute("PRAGMA cipher_page_size = 4096")
    
    return engine
```

#### 2.2 파일 암호화 (Fernet)

```python
# backend/security/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class FileEncryption:
    """파일 암호화/복호화 클래스"""
    
    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """비밀번호로부터 암호화 키 생성"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt_file(file_path: str, password: str) -> str:
        """파일 암호화"""
        # 키 생성
        key, salt = FileEncryption.generate_key(password)
        fernet = Fernet(key)
        
        # 파일 읽기
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # 암호화
        encrypted_data = fernet.encrypt(data)
        
        # 암호화된 파일 저장 (salt + encrypted_data)
        encrypted_path = f"{file_path}.enc"
        with open(encrypted_path, 'wb') as f:
            f.write(salt + encrypted_data)
        
        return encrypted_path
    
    @staticmethod
    def decrypt_file(encrypted_path: str, password: str, output_path: str):
        """파일 복호화"""
        # 암호화된 파일 읽기
        with open(encrypted_path, 'rb') as f:
            salt = f.read(16)
            encrypted_data = f.read()
        
        # 키 생성
        key, _ = FileEncryption.generate_key(password, salt)
        fernet = Fernet(key)
        
        # 복호화
        try:
            decrypted_data = fernet.decrypt(encrypted_data)
        except Exception as e:
            raise ValueError("잘못된 비밀번호 또는 손상된 파일")
        
        # 복호화된 파일 저장
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
```

#### 2.3 비밀번호 해싱 (bcrypt)

```python
# backend/security/auth.py
import bcrypt

class PasswordManager:
    """비밀번호 관리 클래스"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호 해싱"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
```

### 3. 접근 제어

#### 3.1 사용자 인증

```typescript
// frontend/src/services/auth.ts
interface AuthState {
  isAuthenticated: boolean;
  sessionTimeout: number;
  lastActivity: Date;
}

class AuthService {
  private static SESSION_TIMEOUT = 30 * 60 * 1000; // 30분
  
  async login(password: string): Promise<boolean> {
    try {
      // 백엔드에 비밀번호 검증 요청
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });
      
      if (response.ok) {
        // 세션 시작
        this.startSession();
        return true;
      }
      return false;
    } catch (error) {
      console.error('로그인 실패:', error);
      return false;
    }
  }
  
  private startSession() {
    // 세션 타이머 시작
    this.resetActivityTimer();
    
    // 사용자 활동 감지
    window.addEventListener('mousemove', () => this.resetActivityTimer());
    window.addEventListener('keypress', () => this.resetActivityTimer());
  }
  
  private resetActivityTimer() {
    // 마지막 활동 시간 업데이트
    localStorage.setItem('lastActivity', new Date().toISOString());
    
    // 타임아웃 타이머 재설정
    clearTimeout(this.sessionTimer);
    this.sessionTimer = setTimeout(() => {
      this.logout();
      alert('세션이 만료되었습니다. 다시 로그인해주세요.');
    }, AuthService.SESSION_TIMEOUT);
  }
  
  logout() {
    // 세션 종료
    localStorage.removeItem('lastActivity');
    clearTimeout(this.sessionTimer);
    
    // 민감 데이터 메모리에서 제거
    // ... 
  }
}
```

### 4. 데이터 최소화

#### 4.1 필수 정보만 수집

```typescript
// 학생 데이터 모델
interface Student {
  // 필수 정보
  id: string;
  name: string;
  gender: 'M' | 'F';
  
  // 선택 정보 (반편성에 필요한 경우만)
  grade?: number;              // 성적
  characteristics?: string[];  // 특성 (리더십, 조용함 등)
  
  // 민감 정보는 수집하지 않음
  // ❌ 주민등록번호
  // ❌ 주소
  // ❌ 전화번호
  // ❌ 건강 정보
}
```

#### 4.2 자동 삭제 옵션

```python
# backend/api/cleanup.py
from datetime import datetime, timedelta

class DataCleanup:
    """오래된 데이터 자동 삭제"""
    
    @staticmethod
    async def cleanup_old_data(days: int = 365):
        """지정된 기간보다 오래된 데이터 삭제"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 오래된 프로젝트 삭제
        # (사용자 설정에 따라)
        pass
```

### 5. 보안 체크리스트

#### 개발 단계
- [ ] 모든 민감 데이터 암호화
- [ ] SQL 인젝션 방지 (ORM 사용)
- [ ] XSS 방지 (입력 검증)
- [ ] CSRF 방지 (로컬 앱이므로 해당 없음)
- [ ] 안전한 난수 생성 (os.urandom)
- [ ] 비밀번호 평문 저장 금지
- [ ] 로그에 민감 정보 기록 금지

#### 배포 단계
- [ ] 코드 난독화
- [ ] 디버그 모드 비활성화
- [ ] 불필요한 권한 제거
- [ ] 보안 업데이트 메커니즘
- [ ] 취약점 스캔

#### 사용자 가이드
- [ ] 강력한 비밀번호 사용 권장
- [ ] 정기적인 백업 권장
- [ ] 의심스러운 활동 보고 방법
- [ ] 데이터 삭제 방법 안내

### 6. 보안 모범 사례

#### 6.1 비밀번호 정책
```
최소 길이: 8자
권장 길이: 12자 이상
포함 요소: 영문 대소문자, 숫자, 특수문자
금지: 연속된 문자, 생일, 이름 등
```

#### 6.2 키 관리
```rust
// src-tauri/src/encryption.rs
use tauri::api::keyring::Keyring;

// 안전한 키 저장소 사용
fn store_encryption_key(key: &str) -> Result<(), String> {
    let keyring = Keyring::new("aichangeclass", "encryption_key");
    keyring.set_password(key)
        .map_err(|e| format!("키 저장 실패: {}", e))
}

fn retrieve_encryption_key() -> Result<String, String> {
    let keyring = Keyring::new("aichangeclass", "encryption_key");
    keyring.get_password()
        .map_err(|e| format!("키 조회 실패: {}", e))
}
```

#### 6.3 메모리 보안
```python
# 민감 데이터 사용 후 즉시 삭제
import gc

def process_sensitive_data(password: str):
    try:
        # 비밀번호 사용
        result = do_something(password)
        return result
    finally:
        # 메모리에서 제거
        del password
        gc.collect()
```

### 7. 보안 감사 로그

```python
# backend/security/audit.py
import logging
from datetime import datetime

class SecurityAudit:
    """보안 감사 로그"""
    
    @staticmethod
    def log_event(event_type: str, details: dict):
        """보안 이벤트 기록"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
        }
        
        # 민감 정보는 로그에 기록하지 않음
        # ❌ 비밀번호
        # ❌ 암호화 키
        # ❌ 개인정보
        
        logging.info(f"Security Event: {log_entry}")

# 사용 예시
SecurityAudit.log_event('LOGIN_SUCCESS', {'user': 'admin'})
SecurityAudit.log_event('BACKUP_CREATED', {'size': '2.3MB'})
SecurityAudit.log_event('DATA_EXPORT', {'format': 'excel'})
```

---

**문서 버전**: 1.0  
**최종 수정일**: 2024-01-20

