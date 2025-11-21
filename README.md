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

## 🚀 빠른 시작

### Tauri 앱 실행 (권장) ⭐

```bash
# 1. Frontend 디렉토리로 이동
cd frontend

# 2. 의존성 설치 (최초 1회)
npm install

# 3. Tauri 앱 실행 (백엔드 자동 시작!)
npm run tauri:dev
```

**완료!** 앱이 실행되면 백엔드도 자동으로 시작됩니다.

자세한 내용은 [RUN_GUIDE.md](./RUN_GUIDE.md)를 참조하세요.

## 🎯 주요 기능

### 📊 유연한 데이터 관리
- **Excel 파일 업로드**: 드래그 앤 드롭으로 간편하게
- **고정 필드**: 학년, 반, 번호, 이름, 성별 (필수)
- **동적 필드**: 학교마다 자유롭게 추가 가능
  - 예: 성적, 특기, 장애여부, 리더십점수, 교우관계점수 등
  - Excel 파일의 컬럼을 자동으로 인식하여 필드 생성

### ⚙️ 커스텀 반편성 규칙
학교별로 고유한 반편성 규칙을 정의할 수 있습니다:

1. **균형 규칙**: 성별, 성적 등의 균형 유지
2. **제약 규칙**: 특정 학생들의 분리/결합
3. **분산 규칙**: 특정 조건의 학생 고르게 분산
4. **복합 규칙**: 여러 조건을 조합한 고급 규칙

각 규칙에 우선순위와 가중치를 설정하여 학교의 방침에 맞게 조정 가능!

### 🤖 지능형 반편성 알고리즘
- **무작위 배정**: 기준선
- **탐욕 알고리즘**: 빠른 결과
- **유전 알고리즘**: 최적화된 결과 (권장)
- 규칙 기반 자동 평가 및 점수화

### 📈 시각화 및 분석
- 반별 통계 자동 계산
- 규칙별 점수 확인
- 균형도 시각화
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
- [x] 유연한 데이터 스키마 설계
- [x] Excel 업로드 및 파싱 기능
- [x] 커스텀 규칙 엔진 설계
- [x] 반편성 알고리즘 구현 (Random, Greedy, Genetic)
- [x] Backend API 구현
- [x] Frontend UI 개발 (Tauri + React)
- [x] 백엔드 자동 실행 기능
- [ ] LLM 통합 (선택적)
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

