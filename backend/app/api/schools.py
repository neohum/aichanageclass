"""
학교 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..core.database import get_db
from ..models.school import School

router = APIRouter()


class SchoolCreate(BaseModel):
    """학교 생성 요청"""
    name: str
    custom_field_definitions: list = []
    settings: dict = {}


class SchoolResponse(BaseModel):
    """학교 응답"""
    id: int
    name: str
    custom_field_definitions: list
    settings: dict
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[SchoolResponse])
def get_schools(db: Session = Depends(get_db)):
    """학교 목록 조회"""
    schools = db.query(School).all()
    return schools


@router.post("/", response_model=SchoolResponse)
def create_school(school: SchoolCreate, db: Session = Depends(get_db)):
    """학교 생성"""
    db_school = School(**school.dict())
    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    return db_school


@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(school_id: int, db: Session = Depends(get_db)):
    """학교 조회"""
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="학교를 찾을 수 없습니다")
    return school


@router.put("/{school_id}", response_model=SchoolResponse)
def update_school(school_id: int, school: SchoolCreate, db: Session = Depends(get_db)):
    """학교 수정"""
    db_school = db.query(School).filter(School.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="학교를 찾을 수 없습니다")
    
    for key, value in school.dict().items():
        setattr(db_school, key, value)
    
    db.commit()
    db.refresh(db_school)
    return db_school

