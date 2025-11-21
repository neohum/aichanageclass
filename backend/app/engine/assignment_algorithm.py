"""
반편성 알고리즘
"""
from typing import List, Dict, Tuple
import random
import numpy as np
import logging
from ..models.student import Student
from ..models.rule import ClassAssignmentRule
from .rule_engine import RuleEngine

logger = logging.getLogger(__name__)


class AssignmentAlgorithm:
    """반편성 알고리즘"""
    
    def __init__(self, students: List[Student], rules: List[ClassAssignmentRule], num_classes: int):
        """
        Args:
            students: 학생 리스트
            rules: 규칙 리스트
            num_classes: 반 개수
        """
        self.students = students
        self.rules = rules
        self.num_classes = num_classes
        self.rule_engine = RuleEngine(students, rules)
        
        logger.info(f"AssignmentAlgorithm 초기화: {len(students)}명 → {num_classes}개 반")
    
    def generate_assignment(self, method: str = 'genetic', iterations: int = 1000) -> Dict[int, List[Student]]:
        """
        반편성 생성
        
        Args:
            method: 'random', 'greedy', 'genetic'
            iterations: 반복 횟수
            
        Returns:
            {반번호: [학생들]} 형태의 딕셔너리
        """
        if method == 'random':
            return self._random_assignment()
        elif method == 'greedy':
            return self._greedy_assignment()
        elif method == 'genetic':
            return self._genetic_assignment(iterations)
        else:
            raise ValueError(f"알 수 없는 방법: {method}")
    
    def _random_assignment(self) -> Dict[int, List[Student]]:
        """무작위 배정"""
        students_copy = self.students.copy()
        random.shuffle(students_copy)
        
        assignment = {i: [] for i in range(1, self.num_classes + 1)}
        
        for idx, student in enumerate(students_copy):
            class_num = (idx % self.num_classes) + 1
            assignment[class_num].append(student)
        
        return assignment
    
    def _greedy_assignment(self) -> Dict[int, List[Student]]:
        """탐욕 알고리즘 - 규칙을 고려하여 순차적으로 배정"""
        assignment = {i: [] for i in range(1, self.num_classes + 1)}
        students_copy = self.students.copy()
        
        # 우선순위가 높은 규칙부터 처리
        # 1. 성별 균형을 위해 성별로 정렬
        students_copy.sort(key=lambda s: (s.gender, random.random()))
        
        for student in students_copy:
            # 각 반에 배정했을 때의 점수 계산
            best_class = None
            best_score = -1
            
            for class_num in range(1, self.num_classes + 1):
                # 임시 배정
                assignment[class_num].append(student)
                
                # 점수 계산
                result = self.rule_engine.evaluate_assignment(assignment)
                score = result['total_score']
                
                if score > best_score:
                    best_score = score
                    best_class = class_num
                
                # 임시 배정 취소
                assignment[class_num].pop()
            
            # 최적의 반에 배정
            assignment[best_class].append(student)
        
        return assignment
    
    def _genetic_assignment(self, iterations: int = 1000) -> Dict[int, List[Student]]:
        """유전 알고리즘"""
        population_size = 50
        mutation_rate = 0.1
        
        # 초기 개체군 생성
        population = [self._random_assignment() for _ in range(population_size)]
        
        best_assignment = None
        best_score = -1
        
        for iteration in range(iterations):
            # 평가
            scores = []
            for assignment in population:
                result = self.rule_engine.evaluate_assignment(assignment)
                score = result['total_score']
                scores.append(score)
                
                if score > best_score:
                    best_score = score
                    best_assignment = assignment
            
            if iteration % 100 == 0:
                logger.info(f"반복 {iteration}/{iterations}: 최고 점수 = {best_score:.2f}")
            
            # 조기 종료 (점수가 충분히 높으면)
            if best_score >= 95:
                logger.info(f"목표 점수 달성! (반복 {iteration})")
                break
            
            # 선택 (상위 50%)
            sorted_indices = np.argsort(scores)[::-1]
            elite_size = population_size // 2
            elite_indices = sorted_indices[:elite_size]
            
            # 새로운 세대 생성
            new_population = [population[i] for i in elite_indices]
            
            # 교차 및 돌연변이
            while len(new_population) < population_size:
                # 부모 선택
                parent1 = population[random.choice(elite_indices)]
                parent2 = population[random.choice(elite_indices)]
                
                # 교차
                child = self._crossover(parent1, parent2)
                
                # 돌연변이
                if random.random() < mutation_rate:
                    child = self._mutate(child)
                
                new_population.append(child)
            
            population = new_population
        
        logger.info(f"최종 점수: {best_score:.2f}")
        return best_assignment
    
    def _crossover(self, parent1: Dict[int, List[Student]], 
                   parent2: Dict[int, List[Student]]) -> Dict[int, List[Student]]:
        """교차 연산"""
        child = {i: [] for i in range(1, self.num_classes + 1)}
        
        for student in self.students:
            # 부모 중 하나에서 무작위로 선택
            if random.random() < 0.5:
                # parent1에서 학생이 속한 반 찾기
                for class_num, students in parent1.items():
                    if student in students:
                        child[class_num].append(student)
                        break
            else:
                # parent2에서 학생이 속한 반 찾기
                for class_num, students in parent2.items():
                    if student in students:
                        child[class_num].append(student)
                        break
        
        return child
    
    def _mutate(self, assignment: Dict[int, List[Student]]) -> Dict[int, List[Student]]:
        """돌연변이 연산 - 일부 학생의 반을 변경"""
        mutated = {k: v.copy() for k, v in assignment.items()}
        
        # 5% 학생의 반을 변경
        num_mutations = max(1, len(self.students) // 20)
        
        for _ in range(num_mutations):
            # 무작위 학생 선택
            student = random.choice(self.students)
            
            # 현재 반 찾기
            current_class = None
            for class_num, students in mutated.items():
                if student in students:
                    current_class = class_num
                    break
            
            if current_class is None:
                continue
            
            # 다른 반으로 이동
            new_class = random.choice([c for c in range(1, self.num_classes + 1) if c != current_class])
            
            mutated[current_class].remove(student)
            mutated[new_class].append(student)
        
        return mutated

