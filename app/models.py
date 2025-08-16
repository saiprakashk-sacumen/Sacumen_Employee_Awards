from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, Boolean, Float
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(150))
    password_hash = Column(String(256))
    role = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(150))
    project = Column(String(100))
    manager_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Nomination(Base):
    __tablename__ = "nominations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(100))
    justification_text = Column(Text)
    customer_email = Column(String(150))
    core_value = Column(String(50))
    rating = Column(Integer)
    nominee_id = Column(Integer)
    manager_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())

class SentimentResult(Base):
    __tablename__ = "sentiment_results"
    nomination_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer)
    manager_id = Column(Integer)
    sentiment_label = Column(String(20))
    sentiment_score = Column(Float)
    predicted_core_value = Column(String(50))
    core_value_alignment = Column(Integer)
    analyzed_at = Column(TIMESTAMP)

class PasswordReset(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    reset_token = Column(String(256))
    expires_at = Column(TIMESTAMP)
    used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
