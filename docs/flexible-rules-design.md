# 유연한 반편성 규칙 시스템 설계

## 📋 핵심 요구사항

### 1. 학생 데이터 구조
- **고정 필드** (필수): 학년, 반, 번호, 이름, 성별
- **동적 필드** (선택): 학교마다 자유롭게 추가 가능
  - 예: 성적, 특기, 장애여부, 리더십점수, 교우관계점수, 특별관리대상 등

### 2. 반편성 규칙
- **학교별 커스텀 규칙** 정의 가능
- **규칙 우선순위** 설정
- **규칙 유형**:
  - 균형 규칙 (성별, 성적, 특성 등)
  - 제약 규칙 (분리, 결합, 분산 등)
  - 가중치 규칙 (각 규칙의 중요도)

### 3. 오프라인 동작
- 기본 기능은 완전 오프라인
- LLM은 선택적 (복잡한 규칙 해석, 자연어 규칙 입력 시에만)

---

## 🗄 데이터 모델 설계

### 학생 데이터 (Student)

```python
# backend/models/student.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Student(Base):
    """학생 정보 - 유연한 스키마"""
    __tablename__ = 'students'
    
    # 고정 필드 (필수)
    id = Column(Integer, primary_key=True)
    grade = Column(Integer, nullable=False)      # 학년
    original_class = Column(Integer)             # 원래 반 (참고용)
    number = Column(Integer)                     # 번호
    name = Column(String(100), nullable=False)   # 이름
    gender = Column(String(10), nullable=False)  # 성별 (남/여)
    
    # 동적 필드 (JSON으로 저장)
    custom_fields = Column(JSON, default={})
    # 예: {
    #   "성적": 85,
    #   "특기": "운동",
    #   "장애여부": "없음",
    #   "리더십점수": 4,
    #   "특별관리": false
    # }
    
    # 메타데이터
    school_id = Column(Integer, ForeignKey('schools.id'))
    year = Column(Integer)  # 학년도
```

### 학교 설정 (School)

```python
class School(Base):
    """학교 정보 및 설정"""
    __tablename__ = 'schools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    
    # 커스텀 필드 정의
    custom_field_definitions = Column(JSON, default=[])
    # 예: [
    #   {"name": "성적", "type": "number", "min": 0, "max": 100},
    #   {"name": "특기", "type": "text", "options": ["운동", "예술", "학습"]},
    #   {"name": "장애여부", "type": "boolean"},
    #   {"name": "리더십점수", "type": "number", "min": 1, "max": 5}
    # ]
```

### 반편성 규칙 (ClassAssignmentRule)

```python
class ClassAssignmentRule(Base):
    """반편성 규칙"""
    __tablename__ = 'assignment_rules'
    
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'))
    name = Column(String(200))  # 규칙 이름
    
    rule_type = Column(String(50))  # 'balance', 'constraint', 'distribution'
    priority = Column(Integer, default=0)  # 우선순위 (높을수록 중요)
    weight = Column(Float, default=1.0)    # 가중치
    
    # 규칙 정의 (JSON)
    rule_definition = Column(JSON)
    # 예시는 아래 참조
    
    is_active = Column(Boolean, default=True)
```

---

## 🎯 규칙 정의 예시

### 1. 균형 규칙 (Balance Rules)

```json
{
  "type": "balance",
  "field": "gender",
  "target": "equal",
  "tolerance": 2,
  "description": "각 반의 남녀 비율을 최대한 동일하게 (±2명 허용)"
}
```

```json
{
  "type": "balance",
  "field": "성적",
  "target": "average",
  "tolerance": 5,
  "description": "각 반의 평균 성적 차이를 5점 이내로"
}
```

### 2. 제약 규칙 (Constraint Rules)

```json
{
  "type": "constraint",
  "constraint_type": "separate",
  "students": [
    {"name": "홍길동"},
    {"name": "김철수"}
  ],
  "description": "홍길동과 김철수는 다른 반으로"
}
```

```json
{
  "type": "constraint",
  "constraint_type": "together",
  "students": [
    {"name": "이영희"},
    {"name": "박민지"}
  ],
  "description": "이영희와 박민지는 같은 반으로"
}
```

### 3. 분산 규칙 (Distribution Rules)

```json
{
  "type": "distribution",
  "field": "특별관리",
  "value": true,
  "strategy": "spread",
  "max_per_class": 3,
  "description": "특별관리 대상 학생은 각 반에 최대 3명까지 분산"
}
```

```json
{
  "type": "distribution",
  "field": "리더십점수",
  "range": [4, 5],
  "strategy": "spread",
  "description": "리더십 점수 높은 학생(4-5점)을 각 반에 고르게 분산"
}
```

### 4. 복합 규칙 (Complex Rules)

```json
{
  "type": "complex",
  "conditions": [
    {
      "field": "성적",
      "operator": ">=",
      "value": 90
    },
    {
      "field": "특기",
      "operator": "==",
      "value": "학습"
    }
  ],
  "action": {
    "type": "distribution",
    "strategy": "spread",
    "max_per_class": 2
  },
  "description": "성적 90점 이상이면서 특기가 학습인 학생은 각 반에 최대 2명"
}
```

---

## 🔧 규칙 엔진 구조

### RuleEngine 클래스

```python
# backend/engine/rule_engine.py
from typing import List, Dict
import numpy as np
from ..models.student import Student
from ..models.assignment_rules import ClassAssignmentRule

class RuleEngine:
    """반편성 규칙 엔진"""
    
    def __init__(self, students: List[Student], rules: List[ClassAssignmentRule]):
        self.students = students
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        
    def evaluate_assignment(self, assignment: Dict[int, List[Student]]) -> float:
        """
        반편성 결과를 평가
        
        Args:
            assignment: {반번호: [학생들]} 형태의 딕셔너리
            
        Returns:
            점수 (0-100, 높을수록 좋음)
        """
        total_score = 0
        total_weight = 0
        
        for rule in self.rules:
            if not rule.is_active:
                continue
                
            score = self._evaluate_rule(rule, assignment)
            total_score += score * rule.weight
            total_weight += rule.weight
        
        return (total_score / total_weight) if total_weight > 0 else 0
    
    def _evaluate_rule(self, rule: ClassAssignmentRule, 
                       assignment: Dict[int, List[Student]]) -> float:
        """개별 규칙 평가"""
        rule_def = rule.rule_definition
        
        if rule_def['type'] == 'balance':
            return self._evaluate_balance_rule(rule_def, assignment)
        elif rule_def['type'] == 'constraint':
            return self._evaluate_constraint_rule(rule_def, assignment)
        elif rule_def['type'] == 'distribution':
            return self._evaluate_distribution_rule(rule_def, assignment)
        elif rule_def['type'] == 'complex':
            return self._evaluate_complex_rule(rule_def, assignment)
        
        return 0
    
    def _evaluate_balance_rule(self, rule_def: dict, 
                               assignment: Dict[int, List[Student]]) -> float:
        """균형 규칙 평가"""
        field = rule_def['field']
        tolerance = rule_def.get('tolerance', 0)
        
        # 각 반의 필드 값 계산
        class_values = []
        for class_num, students in assignment.items():
            if field == 'gender':
                # 성별 균형: 남학생 수
                value = sum(1 for s in students if s.gender == '남')
            else:
                # 숫자 필드: 평균
                values = [s.custom_fields.get(field, 0) for s in students]
                value = np.mean(values) if values else 0
            class_values.append(value)
        
        # 표준편차 계산
        std_dev = np.std(class_values)
        
        # 점수 계산 (표준편차가 작을수록 높은 점수)
        if std_dev <= tolerance:
            return 100
        else:
            return max(0, 100 - (std_dev - tolerance) * 10)
    
    def _evaluate_constraint_rule(self, rule_def: dict,
                                  assignment: Dict[int, List[Student]]) -> float:
        """제약 규칙 평가"""
        constraint_type = rule_def['constraint_type']
        student_names = [s['name'] for s in rule_def['students']]
        
        # 학생들이 어느 반에 배정되었는지 찾기
        student_classes = {}
        for class_num, students in assignment.items():
            for student in students:
                if student.name in student_names:
                    student_classes[student.name] = class_num
        
        if constraint_type == 'separate':
            # 분리: 모두 다른 반이어야 함
            classes = list(student_classes.values())
            if len(classes) == len(set(classes)):
                return 100  # 모두 다른 반
            else:
                return 0    # 같은 반에 있음
        
        elif constraint_type == 'together':
            # 결합: 모두 같은 반이어야 함
            classes = list(student_classes.values())
            if len(set(classes)) == 1:
                return 100  # 모두 같은 반
            else:
                return 0    # 다른 반에 있음
        
        return 0
```

---

## 📊 Excel 업로드 처리

### Excel 파서

```python
# backend/services/excel_parser.py
import pandas as pd
from typing import List, Dict, Tuple

class ExcelParser:
    """Excel 파일 파싱 및 검증"""
    
    REQUIRED_COLUMNS = ['학년', '반', '번호', '이름', '성별']
    
    @staticmethod
    def parse_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
        """
        Excel 파일 파싱
        
        Returns:
            (학생 데이터 리스트, 커스텀 컬럼 리스트)
        """
        df = pd.read_excel(file_path)
        
        # 필수 컬럼 확인
        missing_cols = [col for col in ExcelParser.REQUIRED_COLUMNS 
                       if col not in df.columns]
        if missing_cols:
            raise ValueError(f"필수 컬럼이 없습니다: {missing_cols}")
        
        # 커스텀 컬럼 추출
        custom_columns = [col for col in df.columns 
                         if col not in ExcelParser.REQUIRED_COLUMNS]
        
        # 데이터 변환
        students = []
        for idx, row in df.iterrows():
            student_data = {
                'grade': int(row['학년']),
                'original_class': int(row['반']) if pd.notna(row['반']) else None,
                'number': int(row['번호']) if pd.notna(row['번호']) else None,
                'name': str(row['이름']),
                'gender': str(row['성별']),
                'custom_fields': {}
            }
            
            # 커스텀 필드 추가
            for col in custom_columns:
                value = row[col]
                if pd.notna(value):
                    student_data['custom_fields'][col] = value
            
            students.append(student_data)
        
        return students, custom_columns
    
    @staticmethod
    def validate_data(students: List[Dict]) -> List[str]:
        """데이터 검증"""
        errors = []
        
        for idx, student in enumerate(students, 1):
            # 이름 확인
            if not student['name'] or student['name'].strip() == '':
                errors.append(f"행 {idx}: 이름이 비어있습니다")
            
            # 성별 확인
            if student['gender'] not in ['남', '여', 'M', 'F']:
                errors.append(f"행 {idx}: 성별이 올바르지 않습니다 ({student['gender']})")
            
            # 학년 확인
            if student['grade'] < 1 or student['grade'] > 6:
                errors.append(f"행 {idx}: 학년이 올바르지 않습니다 ({student['grade']})")
        
        return errors
```

---

## 🎨 UI 설계

### 1. 규칙 설정 화면

```
┌─────────────────────────────────────────────┐
│  ⚙️ 반편성 규칙 설정                         │
├─────────────────────────────────────────────┤
│                                             │
│  📋 규칙 목록                                │
│  ┌───────────────────────────────────────┐ │
│  │ ☑ 성별 균형 (우선순위: 10)            │ │
│  │   각 반의 남녀 비율 동일하게           │ │
│  │   [수정] [삭제]                        │ │
│  ├───────────────────────────────────────┤ │
│  │ ☑ 성적 균형 (우선순위: 8)             │ │
│  │   각 반의 평균 성적 차이 5점 이내      │ │
│  │   [수정] [삭제]                        │ │
│  ├───────────────────────────────────────┤ │
│  │ ☑ 특별관리 학생 분산 (우선순위: 9)    │ │
│  │   각 반에 최대 3명까지                 │ │
│  │   [수정] [삭제]                        │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [+ 새 규칙 추가]                           │
│                                             │
└─────────────────────────────────────────────┘
```

### 2. 규칙 추가 다이얼로그

```
┌─────────────────────────────────────────────┐
│  ➕ 새 규칙 추가                             │
├─────────────────────────────────────────────┤
│  규칙 유형: [균형 규칙 ▼]                   │
│                                             │
│  대상 필드: [성적 ▼]                        │
│  목표: [평균 동일 ▼]                        │
│  허용 오차: [5] 점                          │
│                                             │
│  우선순위: [8] (1-10, 높을수록 중요)        │
│  가중치: [1.0]                              │
│                                             │
│  설명: [각 반의 평균 성적을 비슷하게...]    │
│                                             │
│  [취소] [저장]                              │
└─────────────────────────────────────────────┘
```

---

**다음 단계**: 프로젝트 구조 생성 및 기본 설정 파일 작성

