# Backend - 반편성 AI 시스템

## 🚀 빠른 시작

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate

# 활성화 (Mac/Linux)
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집하여 필요한 설정 변경
```

### 4. 서버 실행

```bash
python main.py
```

서버가 `http://127.0.0.1:8000`에서 실행됩니다.

### 5. API 문서 확인

브라우저에서 다음 주소로 접속:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── api/              # API 엔드포인트
│   │   ├── students.py   # 학생 관리
│   │   ├── schools.py    # 학교 관리
│   │   ├── rules.py      # 규칙 관리
│   │   ├── assignments.py # 반편성 실행
│   │   ├── auth.py       # 인증
│   │   └── backup.py     # 백업
│   ├── core/             # 핵심 설정
│   │   ├── config.py     # 설정
│   │   └── database.py   # 데이터베이스
│   ├── models/           # 데이터 모델
│   │   ├── student.py    # 학생 모델
│   │   ├── school.py     # 학교 모델
│   │   ├── rule.py       # 규칙 모델
│   │   └── assignment.py # 반편성 모델
│   ├── engine/           # 반편성 엔진
│   │   ├── rule_engine.py          # 규칙 평가 엔진
│   │   └── assignment_algorithm.py # 반편성 알고리즘
│   └── services/         # 서비스
│       └── excel_parser.py # Excel 파싱
├── data/                 # 데이터 저장소
├── logs/                 # 로그 파일
├── main.py              # 메인 애플리케이션
├── test_example.py      # 테스트 예제
└── requirements.txt     # 의존성
```

## 🎯 주요 기능

### 1. 유연한 학생 데이터 구조

- **고정 필드**: 학년, 반, 번호, 이름, 성별
- **동적 필드**: 학교마다 자유롭게 추가 가능 (JSON 저장)
  - 예: 성적, 특기, 장애여부, 리더십점수 등

### 2. 커스텀 반편성 규칙

#### 규칙 유형

1. **균형 규칙 (Balance)**
   - 성별, 성적 등의 균형 유지
   - 예: 각 반의 남녀 비율 동일하게

2. **제약 규칙 (Constraint)**
   - 특정 학생들의 분리/결합
   - 예: A와 B는 다른 반으로

3. **분산 규칙 (Distribution)**
   - 특정 조건의 학생 분산
   - 예: 특별관리 학생은 각 반에 최대 3명

4. **복합 규칙 (Complex)**
   - 여러 조건을 조합한 규칙
   - 예: 성적 90점 이상이면서 특기가 학습인 학생 분산

### 3. 반편성 알고리즘

- **Random**: 무작위 배정 (기준선)
- **Greedy**: 탐욕 알고리즘 (빠름)
- **Genetic**: 유전 알고리즘 (최적화, 권장)

## 📝 사용 예제

### Excel 파일 업로드

```python
import requests

# Excel 파일 업로드
with open('students.xlsx', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/students/upload-excel',
        params={'school_id': 1},
        files=files
    )
    print(response.json())
```

### 규칙 생성

```python
# 성별 균형 규칙
rule = {
    "school_id": 1,
    "name": "성별 균형",
    "description": "각 반의 남녀 비율을 동일하게",
    "rule_type": "balance",
    "priority": 10,
    "weight": 1.5,
    "rule_definition": {
        "type": "balance",
        "field": "gender",
        "target": "equal",
        "tolerance": 2
    },
    "is_active": True
}

response = requests.post('http://localhost:8000/api/rules/', json=rule)
```

### 반편성 실행

```python
request = {
    "school_id": 1,
    "grade": 3,
    "year": 2024,
    "num_classes": 3,
    "name": "2024년 3학년 1학기",
    "method": "genetic",
    "iterations": 1000
}

response = requests.post('http://localhost:8000/api/assignments/generate', json=request)
result = response.json()

print(f"총점: {result['total_score']}")
print(f"규칙별 점수: {result['rule_scores']}")
```

## 🧪 테스트

```bash
# 테스트 예제 실행
python test_example.py
```

이 스크립트는:
- 60명의 샘플 학생 데이터 생성
- 4개의 샘플 규칙 생성
- 3가지 알고리즘 비교 (Random, Greedy, Genetic)
- 결과 통계 출력

## 🔧 설정

### 데이터베이스

기본적으로 SQLite를 사용합니다 (`data/aichangeclass.db`).

### 로깅

로그는 `logs/app.log`에 저장됩니다.

### LLM (선택적)

Ollama를 사용하려면:

1. Ollama 설치: https://ollama.ai
2. 모델 다운로드: `ollama pull llama3:8b`
3. `.env`에서 `OLLAMA_ENABLED=True` 설정

## 📚 API 문서

자세한 API 문서는 서버 실행 후 http://127.0.0.1:8000/docs 에서 확인하세요.

## 🐛 문제 해결

### 포트가 이미 사용 중

```bash
# 다른 포트로 실행
uvicorn main:app --port 8001
```

### 데이터베이스 초기화

```bash
# data 폴더 삭제 후 재실행
rm -rf data/
python main.py
```

