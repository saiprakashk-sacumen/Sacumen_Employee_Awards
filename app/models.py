from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .db import Base
from enum import Enum
from datetime import datetime



# Only one Enum needed
class NominationTypeEnum(Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin/manager/etc.
    is_approved = Column(Boolean, default=False, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fetch all employees for a manager easily: current_user.employees
    employees = relationship("Employee", backref="manager")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    project = Column(String(100), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    nominations = relationship("Nomination", backref="employee")


class Nomination(Base):
    __tablename__ = "nominations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(100))
    justification_text = Column(Text)
    customer_email = Column(String(255))
    core_value = Column(String(50))
    rating = Column(Integer)
    nominee_id = Column(String(20), ForeignKey("employees.id"))
    manager_id = Column(Integer, ForeignKey("users.id"))
    nomination_type = Column(
        SQLEnum(NominationTypeEnum, name="nominationtype"),
        nullable=False,
        server_default="monthly"  # default for new rows
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    nomination_id = Column(Integer, primary_key=True, index=True)

    # Existing relationships
    employee_id = Column(String(20), nullable=False)
    manager_id = Column(Integer, nullable=False)

    # New details
    employee_name = Column(String(100), nullable=False)
    manager_name = Column(String(100), nullable=False)
    project_name = Column(String(100), nullable=True)
    nomination_type = Column(String(20), nullable=True)  # monthly, quarterly, yearly etc.

    # Sentiment analysis fields
    sentiment_label = Column(String(20), nullable=True)  # e.g., Positive, Negative
    sentiment_score = Column(Float, nullable=True)
    predicted_core_value = Column(String(50), nullable=True)
    core_value_alignment = Column(Integer, nullable=True)  # alignment score

    # Metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow)


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reset_token = Column(String(256))
    expires_at = Column(DateTime(timezone=True))
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
