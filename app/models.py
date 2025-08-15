import enum
import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Float, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .db import Base

class RoleEnum(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    manager = "manager"

class AwardPeriod(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Employee(Base):
    __tablename__ = "employees"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    department = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ManagerEmployee(Base):
    __tablename__ = "manager_employee"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    relationship_type = Column(String, default="primary")

class AwardCycle(Base):
    __tablename__ = "award_cycles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period = Column(Enum(AwardPeriod), nullable=False)
    cycle_label = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String, default="planned")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

class Nomination(Base):
    __tablename__ = "nominations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id = Column(UUID(as_uuid=True), ForeignKey("award_cycles.id"), nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    project_name = Column(String)
    justification_text = Column(Text)
    customer_email_text = Column(Text, nullable=True)
    customer_email_image_url = Column(String, nullable=True)
    core_value = Column(String) # could be Enum
    rating = Column(Integer)
    status = Column(String, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
