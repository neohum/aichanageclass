"""
반편성 규칙 엔진
"""
from typing import List, Dict, Any
import numpy as np
import logging
from ..models.student import Student
from ..models.rule import ClassAssignmentRule

logger = logging.getLogger(__name__)


class RuleEngine:
    """반편성 규칙 엔진"""
    
    def __init__(self, students: List[Student], rules: List[ClassAssignmentRule]):
        """
        Args:
            students: 학생 리스트
            rules: 규칙 리스트
        """
        self.students = students
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        logger.info(f"RuleEngine 초기화: {len(students)}명 학생, {len(rules)}개 규칙")
    
    def evaluate_assignment(self, assignment: Dict[int, List[Student]]) -> Dict[str, Any]:
        """
        반편성 결과를 평가
        
        Args:
            assignment: {반번호: [학생들]} 형태의 딕셔너리
            
        Returns:
            {
                "total_score": 85.5,
                "rule_scores": {"성별 균형": 95.0, "성적 균형": 76.0},
                "details": {...}
            }
        """
        total_score = 0
        total_weight = 0
        rule_scores = {}
        details = {}
        
        for rule in self.rules:
            if not rule.is_active:
                continue
            
            try:
                score = self._evaluate_rule(rule, assignment)
                rule_scores[rule.name] = round(score, 2)
                total_score += score * rule.weight
                total_weight += rule.weight
                
                logger.debug(f"규칙 '{rule.name}': {score:.2f}점")
            except Exception as e:
                logger.error(f"규칙 '{rule.name}' 평가 오류: {e}")
                rule_scores[rule.name] = 0
        
        final_score = (total_score / total_weight) if total_weight > 0 else 0
        
        return {
            "total_score": round(final_score, 2),
            "rule_scores": rule_scores,
            "details": details
        }
    
    def _evaluate_rule(self, rule: ClassAssignmentRule, 
                       assignment: Dict[int, List[Student]]) -> float:
        """개별 규칙 평가"""
        rule_def = rule.rule_definition
        rule_type = rule_def.get('type')
        
        if rule_type == 'balance':
            return self._evaluate_balance_rule(rule_def, assignment)
        elif rule_type == 'constraint':
            return self._evaluate_constraint_rule(rule_def, assignment)
        elif rule_type == 'distribution':
            return self._evaluate_distribution_rule(rule_def, assignment)
        elif rule_type == 'complex':
            return self._evaluate_complex_rule(rule_def, assignment)
        else:
            logger.warning(f"알 수 없는 규칙 유형: {rule_type}")
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
                # 성별 균형: 남학생 비율
                total = len(students)
                male_count = sum(1 for s in students if s.gender == '남')
                value = (male_count / total * 100) if total > 0 else 50
            else:
                # 숫자 필드: 평균
                values = []
                for s in students:
                    val = s.custom_fields.get(field)
                    if val is not None:
                        values.append(float(val))
                value = np.mean(values) if values else 0
            
            class_values.append(value)
        
        if not class_values:
            return 0
        
        # 표준편차 계산
        std_dev = np.std(class_values)
        
        # 점수 계산 (표준편차가 작을수록 높은 점수)
        if std_dev <= tolerance:
            return 100
        else:
            # 허용 오차를 초과한 만큼 감점
            penalty = (std_dev - tolerance) * 10
            return max(0, 100 - penalty)
    
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
        
        # 모든 학생을 찾지 못한 경우
        if len(student_classes) < len(student_names):
            logger.warning(f"제약 규칙: 일부 학생을 찾을 수 없음 ({student_names})")
            return 50  # 부분 점수
        
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
    
    def _evaluate_distribution_rule(self, rule_def: dict,
                                    assignment: Dict[int, List[Student]]) -> float:
        """분산 규칙 평가"""
        field = rule_def['field']
        max_per_class = rule_def.get('max_per_class', float('inf'))
        
        # 각 반의 해당 학생 수 계산
        class_counts = []
        
        for class_num, students in assignment.items():
            count = 0
            for student in students:
                # 조건 확인
                if 'value' in rule_def:
                    # 특정 값과 일치
                    if student.custom_fields.get(field) == rule_def['value']:
                        count += 1
                elif 'range' in rule_def:
                    # 범위 내
                    val = student.custom_fields.get(field)
                    if val is not None:
                        min_val, max_val = rule_def['range']
                        if min_val <= val <= max_val:
                            count += 1
            
            class_counts.append(count)
        
        # 평가
        # 1. 최대 인원 제한 확인
        if max(class_counts) > max_per_class:
            return 0  # 제한 위반
        
        # 2. 균등 분산 확인
        if not class_counts:
            return 100
        
        std_dev = np.std(class_counts)
        # 표준편차가 1 이하면 만점
        if std_dev <= 1:
            return 100
        else:
            return max(0, 100 - (std_dev - 1) * 20)
    
    def _evaluate_complex_rule(self, rule_def: dict,
                               assignment: Dict[int, List[Student]]) -> float:
        """복합 규칙 평가"""
        conditions = rule_def.get('conditions', [])
        action = rule_def.get('action', {})
        
        # 조건에 맞는 학생 찾기
        matching_students = []
        for students in assignment.values():
            for student in students:
                if self._check_conditions(student, conditions):
                    matching_students.append(student)
        
        # 액션 평가
        if action.get('type') == 'distribution':
            # 분산 규칙으로 평가
            temp_rule_def = {
                'field': '_matched',
                'max_per_class': action.get('max_per_class', float('inf')),
                'strategy': action.get('strategy', 'spread')
            }
            
            # 임시로 매칭된 학생들을 표시
            for student in matching_students:
                student.custom_fields['_matched'] = True
            
            score = self._evaluate_distribution_rule(
                {'field': '_matched', 'value': True, 'max_per_class': action.get('max_per_class', float('inf'))},
                assignment
            )
            
            # 임시 필드 제거
            for student in matching_students:
                student.custom_fields.pop('_matched', None)
            
            return score
        
        return 0
    
    def _check_conditions(self, student: Student, conditions: List[Dict]) -> bool:
        """조건 확인"""
        for condition in conditions:
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            student_value = student.custom_fields.get(field)
            
            if operator == '==':
                if student_value != value:
                    return False
            elif operator == '!=':
                if student_value == value:
                    return False
            elif operator == '>=':
                if student_value is None or student_value < value:
                    return False
            elif operator == '<=':
                if student_value is None or student_value > value:
                    return False
            elif operator == '>':
                if student_value is None or student_value <= value:
                    return False
            elif operator == '<':
                if student_value is None or student_value >= value:
                    return False
        
        return True

