"""
반편성 시스템 테스트 예제
"""
import sys
sys.path.append('.')

from app.models.student import Student
from app.models.rule import ClassAssignmentRule
from app.engine.assignment_algorithm import AssignmentAlgorithm
from app.engine.rule_engine import RuleEngine


def create_sample_students():
    """샘플 학생 데이터 생성"""
    students = []
    
    # 3학년 학생 60명 생성
    for i in range(60):
        student = Student(
            id=i+1,
            grade=3,
            number=i+1,
            name=f"학생{i+1}",
            gender="남" if i % 2 == 0 else "여",
            school_id=1,
            custom_fields={
                "성적": 60 + (i % 40),  # 60-100점 사이
                "특기": ["운동", "예술", "학습"][i % 3],
                "리더십점수": (i % 5) + 1,  # 1-5점
                "특별관리": i % 10 == 0  # 10%
            }
        )
        students.append(student)
    
    return students


def create_sample_rules():
    """샘플 규칙 생성"""
    rules = []
    
    # 1. 성별 균형
    rule1 = ClassAssignmentRule(
        id=1,
        school_id=1,
        name="성별 균형",
        description="각 반의 남녀 비율을 동일하게",
        rule_type="balance",
        priority=10,
        weight=1.5,
        rule_definition={
            "type": "balance",
            "field": "gender",
            "target": "equal",
            "tolerance": 2
        },
        is_active=True
    )
    rules.append(rule1)
    
    # 2. 성적 균형
    rule2 = ClassAssignmentRule(
        id=2,
        school_id=1,
        name="성적 균형",
        description="각 반의 평균 성적을 비슷하게",
        rule_type="balance",
        priority=8,
        weight=1.0,
        rule_definition={
            "type": "balance",
            "field": "성적",
            "target": "average",
            "tolerance": 3
        },
        is_active=True
    )
    rules.append(rule2)
    
    # 3. 특별관리 학생 분산
    rule3 = ClassAssignmentRule(
        id=3,
        school_id=1,
        name="특별관리 학생 분산",
        description="특별관리 학생을 각 반에 고르게",
        rule_type="distribution",
        priority=9,
        weight=1.2,
        rule_definition={
            "type": "distribution",
            "field": "특별관리",
            "value": True,
            "strategy": "spread",
            "max_per_class": 2
        },
        is_active=True
    )
    rules.append(rule3)
    
    # 4. 리더십 학생 분산
    rule4 = ClassAssignmentRule(
        id=4,
        school_id=1,
        name="리더십 학생 분산",
        description="리더십 점수 높은 학생을 각 반에 고르게",
        rule_type="distribution",
        priority=7,
        weight=0.8,
        rule_definition={
            "type": "distribution",
            "field": "리더십점수",
            "range": [4, 5],
            "strategy": "spread"
        },
        is_active=True
    )
    rules.append(rule4)
    
    return rules


def main():
    """메인 테스트"""
    print("=" * 60)
    print("반편성 시스템 테스트")
    print("=" * 60)
    
    # 샘플 데이터 생성
    students = create_sample_students()
    rules = create_sample_rules()
    num_classes = 3
    
    print(f"\n📊 데이터:")
    print(f"  - 학생 수: {len(students)}명")
    print(f"  - 반 개수: {num_classes}개")
    print(f"  - 규칙 수: {len(rules)}개")
    
    print(f"\n📋 규칙:")
    for rule in rules:
        print(f"  - {rule.name} (우선순위: {rule.priority}, 가중치: {rule.weight})")
    
    # 반편성 알고리즘 실행
    print(f"\n🚀 반편성 시작...")
    algorithm = AssignmentAlgorithm(students, rules, num_classes)
    
    # 여러 방법 비교
    methods = [
        ("random", "무작위", 1),
        ("greedy", "탐욕", 1),
        ("genetic", "유전", 500)
    ]
    
    results = []
    
    for method, method_name, iterations in methods:
        print(f"\n--- {method_name} 알고리즘 ---")
        assignment = algorithm.generate_assignment(method=method, iterations=iterations)
        evaluation = algorithm.rule_engine.evaluate_assignment(assignment)
        
        print(f"총점: {evaluation['total_score']:.2f}")
        print(f"규칙별 점수:")
        for rule_name, score in evaluation['rule_scores'].items():
            print(f"  - {rule_name}: {score:.2f}")
        
        # 반별 통계
        print(f"\n반별 통계:")
        for class_num in range(1, num_classes + 1):
            students_in_class = assignment[class_num]
            male_count = sum(1 for s in students_in_class if s.gender == "남")
            female_count = len(students_in_class) - male_count
            
            scores = [s.custom_fields.get("성적", 0) for s in students_in_class]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            special_count = sum(1 for s in students_in_class if s.custom_fields.get("특별관리", False))
            
            print(f"  {class_num}반: {len(students_in_class)}명 (남:{male_count}, 여:{female_count}), "
                  f"평균:{avg_score:.1f}점, 특별관리:{special_count}명")
        
        results.append((method_name, evaluation['total_score']))
    
    # 결과 비교
    print(f"\n" + "=" * 60)
    print("📊 결과 비교")
    print("=" * 60)
    for method_name, score in results:
        print(f"{method_name:10s}: {score:6.2f}점")
    
    best_method = max(results, key=lambda x: x[1])
    print(f"\n🏆 최고 성능: {best_method[0]} ({best_method[1]:.2f}점)")


if __name__ == "__main__":
    main()

