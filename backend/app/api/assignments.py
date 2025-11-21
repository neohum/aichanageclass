"""
반편성 실행 API
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from ..core.database import get_db
from ..models.student import Student
from ..models.rule import ClassAssignmentRule
from ..models.assignment import ClassAssignment, StudentAssignment
from ..engine.assignment_algorithm import AssignmentAlgorithm

router = APIRouter()
logger = logging.getLogger(__name__)


class AssignmentRequest(BaseModel):
    """반편성 요청"""
    school_id: int
    grade: int
    year: int
    num_classes: int
    name: str
    method: str = "genetic"  # random, greedy, genetic
    iterations: int = 1000


class AssignmentResponse(BaseModel):
    """반편성 응답"""
    id: int
    name: str
    grade: int
    year: int
    num_classes: int
    total_score: Optional[float]
    rule_scores: dict
    statistics: dict
    
    class Config:
        from_attributes = True


@router.post("/generate")
def generate_assignment(
    request: AssignmentRequest,
    db: Session = Depends(get_db)
):
    """
    반편성 생성
    """
    # 학생 조회
    students = db.query(Student).filter(
        Student.school_id == request.school_id,
        Student.grade == request.grade
    ).all()
    
    if not students:
        raise HTTPException(status_code=404, detail="학생 데이터가 없습니다")
    
    if len(students) < request.num_classes:
        raise HTTPException(status_code=400, detail="학생 수가 반 개수보다 적습니다")
    
    # 규칙 조회
    rules = db.query(ClassAssignmentRule).filter(
        ClassAssignmentRule.school_id == request.school_id,
        ClassAssignmentRule.is_active == True
    ).all()
    
    logger.info(f"반편성 시작: {len(students)}명 학생, {len(rules)}개 규칙, {request.num_classes}개 반")
    
    # 반편성 알고리즘 실행
    algorithm = AssignmentAlgorithm(students, rules, request.num_classes)
    assignment_result = algorithm.generate_assignment(
        method=request.method,
        iterations=request.iterations
    )
    
    # 평가
    evaluation = algorithm.rule_engine.evaluate_assignment(assignment_result)
    
    # 통계 계산
    statistics = _calculate_statistics(assignment_result)
    
    # 데이터베이스에 저장
    db_assignment = ClassAssignment(
        school_id=request.school_id,
        name=request.name,
        grade=request.grade,
        year=request.year,
        num_classes=request.num_classes,
        total_score=evaluation['total_score'],
        rule_scores=evaluation['rule_scores'],
        statistics=statistics
    )
    db.add(db_assignment)
    db.flush()
    
    # 학생별 배정 저장
    for class_num, students_in_class in assignment_result.items():
        for student in students_in_class:
            student_assignment = StudentAssignment(
                assignment_id=db_assignment.id,
                student_id=student.id,
                assigned_class=class_num
            )
            db.add(student_assignment)
    
    db.commit()
    db.refresh(db_assignment)
    
    logger.info(f"반편성 완료: ID={db_assignment.id}, 점수={evaluation['total_score']:.2f}")
    
    return {
        "id": db_assignment.id,
        "total_score": evaluation['total_score'],
        "rule_scores": evaluation['rule_scores'],
        "statistics": statistics,
        "message": "반편성이 완료되었습니다"
    }


@router.get("/", response_model=List[AssignmentResponse])
def get_assignments(school_id: int, db: Session = Depends(get_db)):
    """반편성 목록 조회"""
    assignments = db.query(ClassAssignment).filter(
        ClassAssignment.school_id == school_id
    ).order_by(ClassAssignment.created_at.desc()).all()
    return assignments


@router.get("/{assignment_id}")
def get_assignment_detail(assignment_id: int, db: Session = Depends(get_db)):
    """반편성 상세 조회"""
    assignment = db.query(ClassAssignment).filter(
        ClassAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="반편성을 찾을 수 없습니다")
    
    # 학생별 배정 조회
    student_assignments = db.query(StudentAssignment).filter(
        StudentAssignment.assignment_id == assignment_id
    ).all()
    
    # 반별로 그룹화
    classes = {}
    for sa in student_assignments:
        if sa.assigned_class not in classes:
            classes[sa.assigned_class] = []
        
        student = db.query(Student).filter(Student.id == sa.student_id).first()
        if student:
            classes[sa.assigned_class].append(student.to_dict())
    
    return {
        "assignment": assignment,
        "classes": classes
    }


@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """반편성 삭제"""
    assignment = db.query(ClassAssignment).filter(
        ClassAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="반편성을 찾을 수 없습니다")
    
    db.delete(assignment)
    db.commit()
    
    return {"message": "반편성이 삭제되었습니다"}


def _calculate_statistics(assignment: dict) -> dict:
    """통계 계산"""
    statistics = {
        "total_students": 0,
        "class_sizes": {},
        "gender_distribution": {},
        "average_scores": {}
    }
    
    for class_num, students in assignment.items():
        statistics["total_students"] += len(students)
        statistics["class_sizes"][class_num] = len(students)
        
        # 성별 분포
        gender_count = {"남": 0, "여": 0}
        scores = []
        
        for student in students:
            gender_count[student.gender] = gender_count.get(student.gender, 0) + 1
            
            # 성적이 있으면 수집
            if "성적" in student.custom_fields:
                scores.append(student.custom_fields["성적"])
        
        statistics["gender_distribution"][class_num] = gender_count
        
        if scores:
            import numpy as np
            statistics["average_scores"][class_num] = round(np.mean(scores), 2)
    
    return statistics

