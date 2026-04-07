"""
utils/db_manager.py
SQLite database management with SQLAlchemy ORM.
Tables: users, analyses, job_descriptions
"""

import os
import json
import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_analyzer.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    file_name = Column(String(255))
    file_type = Column(String(10))
    ats_score = Column(Float)
    grade = Column(String(5))
    word_count = Column(Integer)
    skills_found = Column(Text)      # JSON string
    sections_found = Column(Text)    # JSON string
    feedback = Column(Text)          # JSON string
    resume_text = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    job_matches = relationship("JobMatch", back_populates="analysis", cascade="all, delete-orphan")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    job_title = Column(String(255))
    company = Column(String(255), nullable=True)
    job_description = Column(Text)
    similarity_score = Column(Float)
    keyword_match_score = Column(Float)
    missing_skills = Column(Text)    # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("Analysis", back_populates="job_matches")


def init_db():
    """Initialize database and create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


# --- User Operations ---

def create_user(username: str, email: str, hashed_password: str) -> Optional[User]:
    """Create a new user."""
    db = SessionLocal()
    try:
        user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        return None
    finally:
        db.close()


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).first()
    finally:
        db.close()


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


# --- Analysis Operations ---

def save_analysis(
    file_name: str,
    file_type: str,
    ats_score: float,
    grade: str,
    word_count: int,
    skills_found: list,
    sections_found: list,
    feedback: list,
    resume_text: str,
    user_id: Optional[int] = None,
) -> Optional[Analysis]:
    """Save a resume analysis to the database."""
    db = SessionLocal()
    try:
        analysis = Analysis(
            user_id=user_id,
            file_name=file_name,
            file_type=file_type,
            ats_score=ats_score,
            grade=grade,
            word_count=word_count,
            skills_found=json.dumps(skills_found),
            sections_found=json.dumps(sections_found),
            feedback=json.dumps(feedback),
            resume_text=resume_text[:10000],  # Limit text size
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    except Exception as e:
        db.rollback()
        return None
    finally:
        db.close()


def get_user_analyses(user_id: int, limit: int = 20) -> list:
    """Get all analyses for a user."""
    db = SessionLocal()
    try:
        analyses = (
            db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .limit(limit)
            .all()
        )
        result = []
        for a in analyses:
            result.append({
                "id": a.id,
                "file_name": a.file_name,
                "ats_score": a.ats_score,
                "grade": a.grade,
                "word_count": a.word_count,
                "skills_found": json.loads(a.skills_found or "[]"),
                "sections_found": json.loads(a.sections_found or "[]"),
                "created_at": a.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        return result
    finally:
        db.close()


def get_analysis_by_id(analysis_id: int) -> Optional[dict]:
    """Get a single analysis by ID."""
    db = SessionLocal()
    try:
        a = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not a:
            return None
        return {
            "id": a.id,
            "file_name": a.file_name,
            "file_type": a.file_type,
            "ats_score": a.ats_score,
            "grade": a.grade,
            "word_count": a.word_count,
            "skills_found": json.loads(a.skills_found or "[]"),
            "sections_found": json.loads(a.sections_found or "[]"),
            "feedback": json.loads(a.feedback or "[]"),
            "resume_text": a.resume_text,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M"),
        }
    finally:
        db.close()


# Initialize DB on import
init_db()
