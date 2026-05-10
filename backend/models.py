from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

class UserRole(PyEnum):
    ADMIN = "admin"
    DIRECTOR = "director"
    TEACHER = "teacher"
    STAFF = "staff"
    SUPERVISOR = "supervisor"

class SchoolType(PyEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HIGH_SCHOOL = "high_school"
    KINDERGARTEN = "kindergarten"

class AttendanceStatus(PyEnum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

class MovementType(PyEnum):
    TRANSFER = "transfer"
    PROMOTION = "promotion"
    LEAVE = "leave"
    RECRUITMENT = "recruitment"

class InventoryCondition(PyEnum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    mandoubia_id = Column(Integer, nullable=True)
    
    # Relationships
    mandoubia = relationship("Mandoubia", back_populates="users")

class Mandoubia(Base):
    __tablename__ = "mandoubiat"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="mandoubia")
    schools = relationship("School", back_populates="mandoubia")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    cin = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    status = Column(String, nullable=False)
    grade = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    hire_date = Column(Date, nullable=True)
    
    # Relationships
    school = relationship("School", back_populates="employees")
    attendance = relationship("Attendance", back_populates="employee")
    movements = relationship("Movement", back_populates="employee")

class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(SchoolType), nullable=False)
    address = Column(String, nullable=False)
    director = Column(String, nullable=True)
    capacity = Column(Integer, nullable=True)
    mandoubia_id = Column(Integer, ForeignKey("mandoubiat.id"), nullable=False)
    
    # Relationships
    mandoubia = relationship("Mandoubia", back_populates="schools")
    employees = relationship("Employee", back_populates="school")
    students = relationship("Student", back_populates="school")
    attendance = relationship("Attendance", back_populates="school")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    class_name = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    parent_info = Column(Text, nullable=True)
    enrollment_date = Column(Date, nullable=True)
    status = Column(String, nullable=False)
    
    # Relationships
    school = relationship("School", back_populates="students")
    attendance = relationship("Attendance", back_populates="student")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    justification = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance")
    student = relationship("Student", back_populates="attendance")
    school = relationship("School", back_populates="attendance")

class Movement(Base):
    __tablename__ = "movements"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    type = Column(Enum(MovementType), nullable=False)
    date = Column(Date, nullable=False)
    details = Column(Text, nullable=True)
    from_mandoubia_id = Column(Integer, nullable=True)
    to_mandoubia_id = Column(Integer, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="movements")
    from_mandoubia = relationship("Mandoubia", foreign_keys=[from_mandoubia_id])
    to_mandoubia = relationship("Mandoubia", foreign_keys=[to_mandoubia_id])

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    condition = Column(Enum(InventoryCondition), nullable=False)
    mandoubia_id = Column(Integer, ForeignKey("mandoubiat.id"), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mandoubia = relationship("Mandoubia")
