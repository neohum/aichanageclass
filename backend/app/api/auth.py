"""
인증 API (간단한 버전)
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
def login(password: str):
    """로그인 (간단한 버전)"""
    # TODO: 실제 인증 로직 구현
    return {"message": "로그인 성공", "token": "dummy-token"}


@router.post("/logout")
def logout():
    """로그아웃"""
    return {"message": "로그아웃 성공"}

