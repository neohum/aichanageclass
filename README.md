# 🎓 초등학교 반편성 AI 시스템

> 로컬 AI와 데이터 분석을 활용한 초등학교 학급 편성 자동화 윈도우 애플리케이션

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Tauri](https://img.shields.io/badge/Tauri-1.5+-FFC131.svg)](https://tauri.app/)

## ✨ 핵심 가치

### 🔒 개인정보 보호
- **100% 로컬 저장**: 모든 데이터는 사용자의 컴퓨터에만 저장
- **AES-256 암호화**: 데이터베이스 및 백업 파일 암호화
- **외부 전송 없음**: 인터넷을 통한 데이터 전송 일체 없음

### 📡 오프라인 동작
- **인터넷 불필요**: 완전한 오프라인 환경에서 동작
- **로컬 AI**: Ollama 기반 로컬 LLM 사용
- **독립 실행**: 외부 서비스 의존성 없음

### 🎨 사용자 친화성
- **직관적 UI**: 교사들이 쉽게 사용할 수 있는 인터페이스
- **드래그 앤 드롭**: Excel/CSV 파일 간편 업로드
- **실시간 미리보기**: 설정 변경 시 즉시 결과 확인
- **단계별 가이드**: 첫 사용자를 위한 튜토리얼

### 💾 데이터 안전성
- **자동 백업**: 설정 가능한 주기로 자동 백업
- **암호화 백업**: 모든 백업 파일 암호화
- **쉬운 복구**: 클릭 한 번으로 데이터 복구
- **버전 관리**: GFS(Grandfather-Father-Son) 백업 전략

## 🚀 주요 기능

### 📊 데이터 관리
- Excel/CSV 파일 임포트
- 학생 정보 입력 및 관리
- 제약 조건 설정 (분리 희망, 친구 관계 등)

### 🤖 AI 기반 반편성
- 성별, 성적, 특성 균형 자동 조정
- 제약 조건 자동 처리
- 여러 편성안 생성 및 비교
- AI 분석 및 설명 생성

### 📈 시각화 및 리포트
- 반별 통계 차트
- 균형도 점수 계산
- PDF 리포트 생성
- Excel 내보내기

## 🛠 기술 스택

### Frontend
- **Tauri** - 경량 데스크톱 앱 프레임워크
- **React** - UI 라이브러리
- **TypeScript** - 타입 안전성
- **Material-UI** - UI 컴포넌트
- **Recharts** - 데이터 시각화

### Backend
- **Python 3.11+** - 백엔드 언어
- **FastAPI** - REST API 서버
- **SQLite + SQLCipher** - 암호화 데이터베이스
- **SQLAlchemy** - ORM

### AI/ML
- **Ollama** - 로컬 LLM (llama3, mistral)
- **pandas** - 데이터 처리
- **scikit-learn** - 머신러닝
- **optuna** - 최적화

### Security
- **cryptography** - 파일 암호화
- **bcrypt** - 비밀번호 해싱
- **Tauri Secure Storage** - 키 관리

## 📦 설치 및 실행

### 사전 요구사항

```bash
# Node.js 18+
node --version

# Rust
rustc --version

# Python 3.11+
python --version

# Ollama (로컬 AI)
# https://ollama.ai 에서 다운로드
```

### 설치

```bash
# 저장소 클론
git clone https://github.com/neohum/aichangeclass.git
cd aichangeclass

# Frontend 설정
cd frontend
npm install

# Backend 설정
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Ollama 모델 다운로드
ollama pull llama3:8b
```

### 실행

```bash
# Backend 서버 시작
cd backend
python main.py

# Frontend 개발 서버 (새 터미널)
cd frontend
npm run tauri dev
```

## 📚 문서

- [프로젝트 계획서](./docs/project-plan.md) - 전체 프로젝트 개요 및 설계
- [보안 가이드](./docs/security-guide.md) - 보안 및 개인정보 보호
- [백업 가이드](./docs/backup-guide.md) - 백업 및 복구 방법
- [사용자 매뉴얼](./docs/user-manual.md) - 사용 방법 및 FAQ

## 🗺 로드맵

- [x] 프로젝트 계획 및 문서화
- [ ] 개발 환경 설정
- [ ] 기본 UI 프레임워크
- [ ] 학생 데이터 CRUD
- [ ] 반편성 알고리즘
- [ ] AI 통합
- [ ] 보안 및 암호화
- [ ] 자동 백업 시스템
- [ ] 테스트 및 최적화
- [ ] 배포

## 🤝 기여

기여는 언제나 환영합니다! 이슈를 등록하거나 Pull Request를 보내주세요.

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의

- **이메일**: neohum77@gmail.com
- **GitHub Issues**: [이슈 등록](https://github.com/neohum/aichangeclass/issues)

---

**Made with ❤️ for Teachers**

