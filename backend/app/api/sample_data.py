from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.student import Student
from app.models.school import School
from app.models.rule import ClassAssignmentRule
from io import BytesIO
import pandas as pd
import random
from faker import Faker
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter()
fake = Faker('ko_KR')

# 한국 성씨 리스트
KOREAN_SURNAMES = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전']

def generate_korean_name():
    """한국식 이름 생성"""
    surname = random.choice(KOREAN_SURNAMES)
    given_name = fake.first_name()
    return f"{surname}{given_name}"

@router.get("/generate-sample-excel")
async def generate_sample_excel():
    """샘플 Excel 파일 생성 및 다운로드"""
    
    # 반별 학생 수 및 성비 설정
    class_configs = [
        {'class_num': 1, 'total': 23, 'male': 10, 'female': 13},
        {'class_num': 2, 'total': 23, 'male': 11, 'female': 12},
        {'class_num': 3, 'total': 23, 'male': 12, 'female': 11},
        {'class_num': 4, 'total': 23, 'male': 13, 'female': 10},
        {'class_num': 5, 'total': 23, 'male': 14, 'female': 9},
        {'class_num': 6, 'total': 23, 'male': 15, 'female': 8},
        {'class_num': 7, 'total': 23, 'male': 16, 'female': 7},
    ]
    
    students_data = []
    used_names = set()
    twin_pairs = []  # 쌍둥이 쌍 저장
    special_care_students = []  # 특별관리 학생
    twin_students = []  # 쌍둥이 학생 임시 저장 (나중에 상대방 정보 추가용)
    together_pairs = []  # 함께 가야 할 학생 쌍
    separate_pairs = []  # 분리되어야 할 학생 쌍

    # 쌍둥이 5쌍 생성 (10명)
    for i in range(5):
        twin_surname = random.choice(KOREAN_SURNAMES)
        twin_class = random.randint(1, 7)
        twin_gender = random.choice(['남', '여'])
        twin_pairs.append({
            'class': twin_class,
            'surname': twin_surname,
            'gender': twin_gender,
            'pair_id': i + 1
        })

    # 함께 가야 할 학생 5쌍 생성 (10명)
    for i in range(5):
        together_class = random.randint(1, 7)
        together_gender = random.choice(['남', '여'])
        together_pairs.append({
            'class': together_class,
            'gender': together_gender,
            'pair_id': i + 1
        })

    # 분리되어야 할 학생 5쌍 생성 (10명)
    for i in range(5):
        separate_class = random.randint(1, 7)
        separate_gender = random.choice(['남', '여'])
        separate_pairs.append({
            'class': separate_class,
            'gender': separate_gender,
            'pair_id': i + 1
        })
    
    for config in class_configs:
        class_num = config['class_num']
        male_count = config['male']
        female_count = config['female']

        # 이 반의 쌍둥이 확인
        class_twins = [t for t in twin_pairs if t['class'] == class_num]

        # 남학생 번호는 1번부터
        male_student_id = 1

        # 남학생 생성
        for i in range(male_count):
            # 쌍둥이 처리
            is_twin = False
            twin_pair_id = None
            if class_twins and class_twins[0]['gender'] == '남' and i < 2:
                is_twin = True
                twin_info = class_twins[0]
                twin_pair_id = twin_info['pair_id']
                if i == 1:
                    class_twins.pop(0)

            name = generate_korean_name()
            while name in used_names:
                name = generate_korean_name()

            if is_twin and twin_pair_id:
                # 쌍둥이는 같은 성씨 사용
                twin_info = [t for t in twin_pairs if t['pair_id'] == twin_pair_id][0]
                name = f"{twin_info['surname']}{fake.first_name()}"

            used_names.add(name)

            student_data = {
                '학년': 3,
                '반': class_num,
                '번호': male_student_id,
                '이름': name,
                '성별': '남',
                '성적': random.choice(['상', '상', '중', '중', '중', '하']),
                '생활태도': random.choice(['상', '상', '중', '중', '중', '하']),
                '교우관계': random.choice(['상', '상', '중', '중', '중', '하']),
                '특기': random.choice(['축구', '농구', '미술', '음악', '과학', '수학', '영어', '독서', '컴퓨터', '']),
                '쌍둥이': '',  # 나중에 채움
                '함께': '',  # 나중에 채움
                '분리': '',  # 나중에 채움
                '특별관리': '',
                '비고': '',
                '_twin_pair_id': twin_pair_id  # 임시 필드
            }

            students_data.append(student_data)
            if is_twin:
                twin_students.append({
                    'index': len(students_data) - 1,
                    'pair_id': twin_pair_id,
                    'grade': 3,
                    'class': class_num,
                    'number': male_student_id,
                    'name': name
                })
            male_student_id += 1
        
        # 여학생 번호는 41번부터
        female_student_id = 41

        # 여학생 생성
        for i in range(female_count):
            # 쌍둥이 처리
            is_twin = False
            twin_pair_id = None
            if class_twins and class_twins[0]['gender'] == '여' and i < 2:
                is_twin = True
                twin_info = class_twins[0]
                twin_pair_id = twin_info['pair_id']
                if i == 1:
                    class_twins.pop(0)

            name = generate_korean_name()
            while name in used_names:
                name = generate_korean_name()

            if is_twin and twin_pair_id:
                # 쌍둥이는 같은 성씨 사용
                twin_info = [t for t in twin_pairs if t['pair_id'] == twin_pair_id][0]
                name = f"{twin_info['surname']}{fake.first_name()}"

            used_names.add(name)

            student_data = {
                '학년': 3,
                '반': class_num,
                '번호': female_student_id,
                '이름': name,
                '성별': '여',
                '성적': random.choice(['상', '상', '중', '중', '중', '하']),
                '생활태도': random.choice(['상', '상', '중', '중', '중', '하']),
                '교우관계': random.choice(['상', '상', '중', '중', '중', '하']),
                '특기': random.choice(['피아노', '발레', '미술', '음악', '과학', '수학', '영어', '독서', '컴퓨터', '']),
                '쌍둥이': '',  # 나중에 채움
                '함께': '',  # 나중에 채움
                '분리': '',  # 나중에 채움
                '특별관리': '',
                '비고': '',
                '_twin_pair_id': twin_pair_id  # 임시 필드
            }

            students_data.append(student_data)
            if is_twin:
                twin_students.append({
                    'index': len(students_data) - 1,
                    'pair_id': twin_pair_id,
                    'grade': 3,
                    'class': class_num,
                    'number': female_student_id,
                    'name': name
                })
            female_student_id += 1
    
    # 쌍둥이 정보 채우기 (상대방의 학년-반-번호-이름)
    for twin in twin_students:
        pair_id = twin['pair_id']
        # 같은 pair_id를 가진 다른 쌍둥이 찾기
        siblings = [t for t in twin_students if t['pair_id'] == pair_id and t['index'] != twin['index']]
        if siblings:
            sibling = siblings[0]
            # "3-1-5-김철수" 형식으로 저장
            students_data[twin['index']]['쌍둥이'] = f"{sibling['grade']}-{sibling['class']}-{sibling['number']}-{sibling['name']}"

    # 함께 가야 할 학생 쌍 생성 (5쌍, 10명)
    # 쌍둥이가 아닌 학생들 중에서 선택
    non_twin_indices = [i for i, s in enumerate(students_data) if not s.get('_twin_pair_id')]
    together_indices = random.sample(non_twin_indices, min(10, len(non_twin_indices)))

    for i in range(0, len(together_indices), 2):
        if i + 1 < len(together_indices):
            idx1 = together_indices[i]
            idx2 = together_indices[i + 1]
            s1 = students_data[idx1]
            s2 = students_data[idx2]
            # 서로의 정보를 함께 필드에 저장
            students_data[idx1]['함께'] = f"{s2['학년']}-{s2['반']}-{s2['번호']}-{s2['이름']}"
            students_data[idx2]['함께'] = f"{s1['학년']}-{s1['반']}-{s1['번호']}-{s1['이름']}"

    # 분리되어야 할 학생 쌍 생성 (5쌍, 10명)
    # 쌍둥이도 아니고 함께 쌍도 아닌 학생들 중에서 선택
    non_paired_indices = [i for i, s in enumerate(students_data)
                          if not s.get('_twin_pair_id') and not s['함께']]
    separate_indices = random.sample(non_paired_indices, min(10, len(non_paired_indices)))

    for i in range(0, len(separate_indices), 2):
        if i + 1 < len(separate_indices):
            idx1 = separate_indices[i]
            idx2 = separate_indices[i + 1]
            s1 = students_data[idx1]
            s2 = students_data[idx2]
            # 서로의 정보를 분리 필드에 저장
            students_data[idx1]['분리'] = f"{s2['학년']}-{s2['반']}-{s2['번호']}-{s2['이름']}"
            students_data[idx2]['분리'] = f"{s1['학년']}-{s1['반']}-{s1['번호']}-{s1['이름']}"

    # _twin_pair_id 임시 필드 제거
    for student_data in students_data:
        if '_twin_pair_id' in student_data:
            del student_data['_twin_pair_id']

    # 특별관리 학생 10명 랜덤 선택
    special_indices = random.sample(range(len(students_data)), 10)
    special_reasons = ['ADHD', '학습부진', '정서불안', '건강문제', '가정문제', '또래관계어려움']

    for idx in special_indices:
        students_data[idx]['특별관리'] = '예'
        students_data[idx]['비고'] = random.choice(special_reasons)
    
    # DataFrame 생성
    df = pd.DataFrame(students_data)
    
    # Excel 파일로 변환
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='학생명단')
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=sample_students.xlsx'}
    )

@router.post("/load-sample-data/{school_id}")
async def load_sample_data(school_id: int, db: Session = Depends(get_db)):
    """샘플 데이터를 데이터베이스에 로드"""

    # 기존 학생 데이터 삭제
    db.query(Student).filter(Student.school_id == school_id).delete()
    db.commit()

    # 샘플 데이터 생성 (위와 동일한 로직)
    class_configs = [
        {'class_num': 1, 'total': 23, 'male': 10, 'female': 13},
        {'class_num': 2, 'total': 22, 'male': 11, 'female': 11},
        {'class_num': 3, 'total': 24, 'male': 13, 'female': 11},
        {'class_num': 4, 'total': 25, 'male': 14, 'female': 11},
        {'class_num': 5, 'total': 23, 'male': 14, 'female': 9},
        {'class_num': 6, 'total': 21, 'male': 15, 'female': 6},
        {'class_num': 7, 'total': 19, 'male': 12, 'female': 7},
    ]

    used_names = set()
    twin_pairs = []
    students = []
    twin_students = []  # 쌍둥이 학생 임시 저장

    # 쌍둥이 5쌍 생성
    for i in range(5):
        twin_surname = random.choice(KOREAN_SURNAMES)
        twin_class = random.randint(1, 7)
        twin_gender = random.choice(['남', '여'])
        twin_pairs.append({
            'class': twin_class,
            'surname': twin_surname,
            'gender': twin_gender,
            'pair_id': i + 1
        })

    for config in class_configs:
        class_num = config['class_num']
        male_count = config['male']
        female_count = config['female']

        class_twins = [t for t in twin_pairs if t['class'] == class_num]

        # 남학생 번호는 1번부터
        male_student_number = 1

        # 남학생 생성
        for i in range(male_count):
            is_twin = False
            twin_pair_id = None
            if class_twins and class_twins[0]['gender'] == '남' and i < 2:
                is_twin = True
                twin_info = class_twins[0]
                twin_pair_id = twin_info['pair_id']
                if i == 1:
                    class_twins.pop(0)

            name = generate_korean_name()
            while name in used_names:
                name = generate_korean_name()

            if is_twin and twin_pair_id:
                # 쌍둥이는 같은 성씨 사용
                twin_info = [t for t in twin_pairs if t['pair_id'] == twin_pair_id][0]
                name = f"{twin_info['surname']}{fake.first_name()}"

            used_names.add(name)

            custom_fields = {
                '성적': random.choice(['상', '상', '중', '중', '중', '하']),
                '생활태도': random.choice(['상', '상', '중', '중', '중', '하']),
                '교우관계': random.choice(['상', '상', '중', '중', '중', '하']),
                '특기': random.choice(['축구', '농구', '미술', '음악', '과학', '수학', '영어', '독서', '컴퓨터', '']),
                '쌍둥이': '',  # 나중에 채움
                '함께': '',  # 나중에 채움
                '분리': '',  # 나중에 채움
                '특별관리': '',
                '비고': ''
            }

            student = Student(
                school_id=school_id,
                grade=3,
                class_name=str(class_num),
                student_number=male_student_number,
                name=name,
                gender='남',
                custom_fields=custom_fields
            )
            students.append(student)
            if is_twin:
                twin_students.append({
                    'index': len(students) - 1,
                    'pair_id': twin_pair_id,
                    'grade': 3,
                    'class': class_num,
                    'number': male_student_number,
                    'name': name
                })
            male_student_number += 1

        # 여학생 번호는 41번부터
        female_student_number = 41

        # 여학생 생성
        for i in range(female_count):
            is_twin = False
            twin_pair_id = None
            if class_twins and class_twins[0]['gender'] == '여' and i < 2:
                is_twin = True
                twin_info = class_twins[0]
                twin_pair_id = twin_info['pair_id']
                if i == 1:
                    class_twins.pop(0)

            name = generate_korean_name()
            while name in used_names:
                name = generate_korean_name()

            if is_twin and twin_pair_id:
                # 쌍둥이는 같은 성씨 사용
                twin_info = [t for t in twin_pairs if t['pair_id'] == twin_pair_id][0]
                name = f"{twin_info['surname']}{fake.first_name()}"

            used_names.add(name)

            custom_fields = {
                '성적': random.choice(['상', '상', '중', '중', '중', '하']),
                '생활태도': random.choice(['상', '상', '중', '중', '중', '하']),
                '교우관계': random.choice(['상', '상', '중', '중', '중', '하']),
                '특기': random.choice(['피아노', '발레', '미술', '음악', '과학', '수학', '영어', '독서', '컴퓨터', '']),
                '쌍둥이': '',  # 나중에 채움
                '함께': '',  # 나중에 채움
                '분리': '',  # 나중에 채움
                '특별관리': '',
                '비고': ''
            }

            student = Student(
                school_id=school_id,
                grade=3,
                class_name=str(class_num),
                student_number=female_student_number,
                name=name,
                gender='여',
                custom_fields=custom_fields
            )
            students.append(student)
            if is_twin:
                twin_students.append({
                    'index': len(students) - 1,
                    'pair_id': twin_pair_id,
                    'grade': 3,
                    'class': class_num,
                    'number': female_student_number,
                    'name': name
                })
            female_student_number += 1

    # 쌍둥이 정보 채우기 (상대방의 학년-반-번호-이름)
    for twin in twin_students:
        pair_id = twin['pair_id']
        # 같은 pair_id를 가진 다른 쌍둥이 찾기
        siblings = [t for t in twin_students if t['pair_id'] == pair_id and t['index'] != twin['index']]
        if siblings:
            sibling = siblings[0]
            # "3-1-5-김철수" 형식으로 저장
            students[twin['index']].custom_fields['쌍둥이'] = f"{sibling['grade']}-{sibling['class']}-{sibling['number']}-{sibling['name']}"

    # 함께 가야 할 학생 쌍 생성 (5쌍, 10명)
    # 쌍둥이가 아닌 학생들 중에서 선택
    non_twin_indices = [i for i, s in enumerate(students) if not s.custom_fields.get('쌍둥이')]
    together_indices = random.sample(non_twin_indices, min(10, len(non_twin_indices)))

    for i in range(0, len(together_indices), 2):
        if i + 1 < len(together_indices):
            idx1 = together_indices[i]
            idx2 = together_indices[i + 1]
            s1 = students[idx1]
            s2 = students[idx2]
            # 서로의 정보를 함께 필드에 저장
            s1.custom_fields['함께'] = f"{s2.grade}-{s2.class_name}-{s2.student_number}-{s2.name}"
            s2.custom_fields['함께'] = f"{s1.grade}-{s1.class_name}-{s1.student_number}-{s1.name}"

    # 분리되어야 할 학생 쌍 생성 (5쌍, 10명)
    # 쌍둥이도 아니고 함께 쌍도 아닌 학생들 중에서 선택
    non_paired_indices = [i for i, s in enumerate(students)
                          if not s.custom_fields.get('쌍둥이') and not s.custom_fields.get('함께')]
    separate_indices = random.sample(non_paired_indices, min(10, len(non_paired_indices)))

    for i in range(0, len(separate_indices), 2):
        if i + 1 < len(separate_indices):
            idx1 = separate_indices[i]
            idx2 = separate_indices[i + 1]
            s1 = students[idx1]
            s2 = students[idx2]
            # 서로의 정보를 분리 필드에 저장
            s1.custom_fields['분리'] = f"{s2.grade}-{s2.class_name}-{s2.student_number}-{s2.name}"
            s2.custom_fields['분리'] = f"{s1.grade}-{s1.class_name}-{s1.student_number}-{s1.name}"

    # 특별관리 학생 10명 랜덤 선택
    special_indices = random.sample(range(len(students)), 10)
    special_reasons = ['ADHD', '학습부진', '정서불안', '건강문제', '가정문제', '또래관계어려움']

    for idx in special_indices:
        students[idx].custom_fields['특별관리'] = '예'
        students[idx].custom_fields['비고'] = random.choice(special_reasons)

    # DB에 저장
    db.add_all(students)
    db.commit()

    return {
        "message": "샘플 데이터가 성공적으로 로드되었습니다.",
        "total_students": len(students),
        "classes": 7,
        "twins": 10,
        "special_care": 10
    }

@router.post("/create-sample-rules/{school_id}")
async def create_sample_rules(school_id: int, db: Session = Depends(get_db)):
    """샘플 규칙 생성"""

    # 기존 규칙 삭제
    db.query(ClassAssignmentRule).filter(ClassAssignmentRule.school_id == school_id).delete()
    db.commit()

    rules = [
        ClassAssignmentRule(
            school_id=school_id,
            name="성별 균형",
            rule_type="balance",
            priority=10,
            weight=10.0,
            is_active=True,
            rule_definition={
                "field": "성별",
                "target": "equal",
                "tolerance": 2
            }
        ),
        ClassAssignmentRule(
            school_id=school_id,
            name="성적 균형",
            rule_type="balance",
            priority=8,
            weight=8.0,
            is_active=True,
            rule_definition={
                "field": "성적",
                "target": "equal",
                "tolerance": 1
            }
        ),
        ClassAssignmentRule(
            school_id=school_id,
            name="생활태도 균형",
            rule_type="balance",
            priority=7,
            weight=7.0,
            is_active=True,
            rule_definition={
                "field": "생활태도",
                "target": "equal",
                "tolerance": 1
            }
        ),
        ClassAssignmentRule(
            school_id=school_id,
            name="교우관계 균형",
            rule_type="balance",
            priority=6,
            weight=6.0,
            is_active=True,
            rule_definition={
                "field": "교우관계",
                "target": "equal",
                "tolerance": 1
            }
        ),
        ClassAssignmentRule(
            school_id=school_id,
            name="쌍둥이 분리",
            rule_type="constraint",
            priority=10,
            weight=15.0,
            is_active=True,
            rule_definition={
                "constraint_type": "separate",
                "field": "쌍둥이"
            }
        ),
        ClassAssignmentRule(
            school_id=school_id,
            name="함께 배치",
            rule_type="constraint",
            priority=9,
            weight=12.0,
            is_active=True,
            rule_definition={
                "constraint_type": "together",
                "field": "함께"
            }
        ),
        ClassAssignmentRule(
            school_id=school_id,
            name="분리 배치",
            rule_type="constraint",
            priority=9,
            weight=12.0,
            is_active=True,
            rule_definition={
                "constraint_type": "separate",
                "field": "분리"
            }
        ),
        ClassAssignmentRule(
            school_id=school_id,
            name="특별관리 학생 분산",
            rule_type="distribution",
            priority=8,
            weight=9.0,
            is_active=True,
            rule_definition={
                "field": "특별관리",
                "strategy": "spread",
                "max_per_class": 2
            }
        ),
    ]

    db.add_all(rules)
    db.commit()

    return {
        "message": "샘플 규칙이 성공적으로 생성되었습니다.",
        "total_rules": len(rules),
        "rules": [
            "성별 균형",
            "성적 균형",
            "생활태도 균형",
            "교우관계 균형",
            "쌍둥이 분리",
            "함께 배치",
            "분리 배치",
            "특별관리 학생 분산"
        ]
    }


