"""
반편성 규칙 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..core.database import get_db
from ..models.rule import ClassAssignmentRule, RULE_EXAMPLES

router = APIRouter()


class RuleCreate(BaseModel):
    """규칙 생성 요청"""
    school_id: int
    name: str
    description: Optional[str] = None
    rule_type: str
    priority: int = 5
    weight: float = 1.0
    rule_definition: dict
    is_active: bool = True


class RuleResponse(BaseModel):
    """규칙 응답"""
    id: int
    school_id: int
    name: str
    description: Optional[str]
    rule_type: str
    priority: int
    weight: float
    rule_definition: dict
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/examples")
def get_rule_examples():
    """규칙 예시 조회"""
    return RULE_EXAMPLES


@router.get("/", response_model=List[RuleResponse])
def get_rules(school_id: int, db: Session = Depends(get_db)):
    """규칙 목록 조회"""
    rules = db.query(ClassAssignmentRule).filter(
        ClassAssignmentRule.school_id == school_id
    ).order_by(ClassAssignmentRule.priority.desc()).all()
    return rules


@router.post("/", response_model=RuleResponse)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """규칙 생성"""
    db_rule = ClassAssignmentRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, rule: RuleCreate, db: Session = Depends(get_db)):
    """규칙 수정"""
    db_rule = db.query(ClassAssignmentRule).filter(ClassAssignmentRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="규칙을 찾을 수 없습니다")
    
    for key, value in rule.dict().items():
        setattr(db_rule, key, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """규칙 삭제"""
    db_rule = db.query(ClassAssignmentRule).filter(ClassAssignmentRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="규칙을 찾을 수 없습니다")
    
    db.delete(db_rule)
    db.commit()
    return {"message": "규칙이 삭제되었습니다"}


@router.patch("/{rule_id}/toggle")
def toggle_rule(rule_id: int, db: Session = Depends(get_db)):
    """규칙 활성화/비활성화"""
    db_rule = db.query(ClassAssignmentRule).filter(ClassAssignmentRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="규칙을 찾을 수 없습니다")
    
    db_rule.is_active = not db_rule.is_active
    db.commit()
    
    return {"is_active": db_rule.is_active}

