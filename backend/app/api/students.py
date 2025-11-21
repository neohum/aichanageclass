"""
학생 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import tempfile
import os

from ..core.database import get_db
from ..models.student import Student
from ..models.school import School
from ..services.excel_parser import ExcelParser
from pydantic import BaseModel

router = APIRouter()


class StudentCreate(BaseModel):
    """학생 생성 요청"""
    school_id: int
    grade: int
    name: str
    gender: str
    original_class: Optional[int] = None
    number: Optional[int] = None
    custom_fields: dict = {}
    year: int = 2024


class StudentResponse(BaseModel):
    """학생 응답"""
    id: int
    grade: int
    name: str
    gender: str
    original_class: Optional[int]
    number: Optional[int]
    custom_fields: dict
    school_id: int
    year: int
    
    class Config:
        from_attributes = True


@router.post("/upload-excel")
async def upload_excel(
    school_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Excel 파일 업로드 및 학생 데이터 임포트
    """
    # 학교 확인
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="학교를 찾을 수 없습니다")
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Excel 파싱
        students_data, custom_columns, field_definitions = ExcelParser.parse_excel(tmp_file_path)
        
        # 데이터 검증
        errors = ExcelParser.validate_data(students_data)
        if errors:
            return {
                "success": False,
                "errors": errors
            }
        
        # 커스텀 필드 정의 업데이트
        school.custom_field_definitions = field_definitions
        
        # 학생 데이터 저장
        created_students = []
        for student_data in students_data:
            student = Student(
                school_id=school_id,
                **student_data
            )
            db.add(student)
            created_students.append(student)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{len(created_students)}명의 학생 데이터를 임포트했습니다",
            "count": len(created_students),
            "custom_columns": custom_columns,
            "field_definitions": field_definitions
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        # 임시 파일 삭제
        os.unlink(tmp_file_path)


@router.get("/", response_model=List[StudentResponse])
def get_students(
    school_id: int,
    grade: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """학생 목록 조회"""
    query = db.query(Student).filter(Student.school_id == school_id)
    
    if grade:
        query = query.filter(Student.grade == grade)
    
    students = query.all()
    return students


@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """학생 생성"""
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    """학생 수정"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    for key, value in student.dict().items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """학생 삭제"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    db.delete(db_student)
    db.commit()
    return {"message": "학생이 삭제되었습니다"}

