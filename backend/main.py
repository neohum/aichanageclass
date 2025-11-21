"""
초등학교 반편성 AI 시스템 - Backend API Server
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base
from app.api import students, rules, assignments, schools, auth, sample_data

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행"""
    # 시작 시
    logger.info("🚀 애플리케이션 시작")
    
    # 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 데이터베이스 초기화 완료")
    
    # 필요한 디렉토리 생성
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    logger.info("✅ 디렉토리 생성 완료")
    
    yield
    
    # 종료 시
    logger.info("👋 애플리케이션 종료")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="초등학교 반편성을 위한 로컬 AI 기반 시스템",
    lifespan=lifespan
)

# CORS 설정 (Tauri 프론트엔드와 통신)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",  # Tauri 기본 포트
        "http://localhost:5173",  # Vite 개발 서버
        "http://localhost:5174",  # Vite 대체 포트
        "tauri://localhost",      # Tauri 프로토콜
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["인증"])
app.include_router(schools.router, prefix="/api/schools", tags=["학교"])
app.include_router(students.router, prefix="/api/students", tags=["학생"])
app.include_router(rules.router, prefix="/api/rules", tags=["규칙"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["반편성"])
app.include_router(sample_data.router, prefix="/api/sample", tags=["샘플데이터"])


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "초등학교 반편성 AI 시스템 API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    # 개발 서버 실행
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # 로컬에서만 접근 가능
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

