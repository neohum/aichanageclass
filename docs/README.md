# 📚 문서 목록

## 초등학교 반편성 AI 시스템 문서

이 폴더에는 프로젝트의 모든 문서가 포함되어 있습니다.

### 📄 문서 목록

1. **[프로젝트 계획서](./project-plan.md)** 📋
   - 프로젝트 개요 및 목표
   - 기술 스택 및 아키텍처
   - 개발 로드맵
   - 핵심 기능 상세 설계

2. **[보안 가이드](./security-guide.md)** 🔐
   - 개인정보 보호 정책
   - 데이터 암호화 구현
   - 접근 제어 및 인증
   - 보안 모범 사례

3. **[백업 가이드](./backup-guide.md)** 💾
   - 자동 백업 시스템
   - 백업 전략 (GFS)
   - 복구 프로세스
   - 백업 모범 사례

4. **[사용자 매뉴얼](./user-manual.md)** 📖
   - 시작하기
   - 학생 데이터 관리
   - 반편성 실행 방법
   - 문제 해결 (FAQ)

### 🎯 핵심 가치

이 프로젝트는 다음 4가지 핵심 가치를 중심으로 설계되었습니다:

1. **🔒 개인정보 보호**
   - 모든 데이터 로컬 저장
   - AES-256 암호화
   - 외부 서버 전송 없음

2. **📡 오프라인 동작**
   - 인터넷 연결 불필요
   - 로컬 AI 모델 (Ollama)
   - 완전한 독립 실행

3. **🎨 사용자 친화성**
   - 직관적인 UI/UX
   - 드래그 앤 드롭
   - 단계별 가이드

4. **💾 데이터 안전성**
   - 자동 백업
   - 암호화된 백업 파일
   - 쉬운 복구 프로세스

### 🚀 빠른 시작

1. **개발 환경 설정**
   ```bash
   # Node.js, Rust, Python 설치 확인
   node --version
   rustc --version
   python --version
   
   # Tauri CLI 설치
   npm install -g @tauri-apps/cli
   
   # Ollama 설치 (로컬 AI)
   # https://ollama.ai 에서 다운로드
   ```

2. **프로젝트 초기화**
   ```bash
   # Tauri 프로젝트 생성
   npm create tauri-app
   
   # Python 가상환경 생성
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # 의존성 설치
   pip install -r requirements.txt
   ```

3. **문서 읽기 순서**
   - 처음 시작: [프로젝트 계획서](./project-plan.md)
   - 개발자: [보안 가이드](./security-guide.md) → [백업 가이드](./backup-guide.md)
   - 사용자: [사용자 매뉴얼](./user-manual.md)

### 📊 프로젝트 구조

```
aichangeclass/
├── docs/                    # 📚 문서 (현재 위치)
│   ├── README.md           # 문서 목록 (본 파일)
│   ├── project-plan.md     # 프로젝트 계획서
│   ├── security-guide.md   # 보안 가이드
│   ├── backup-guide.md     # 백업 가이드
│   └── user-manual.md      # 사용자 매뉴얼
├── frontend/               # 프론트엔드 (Tauri + React)
├── backend/                # 백엔드 (Python FastAPI)
├── data/                   # 로컬 데이터
└── README.md               # 프로젝트 README
```

### 🔄 문서 업데이트

문서는 프로젝트 진행에 따라 지속적으로 업데이트됩니다.

**최종 업데이트**: 2024-01-20  
**문서 버전**: 1.0

### 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**Happy Coding! 🎉**

