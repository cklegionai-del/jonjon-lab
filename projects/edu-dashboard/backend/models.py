from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    TEACHER = "teacher"
    STUDENT = "student"

class Mandoubia(Base):
    __tablename__ = "mandoubiat"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    code = Column(String(10), unique=True, index=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(200))
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    mandoubia_id = Column(Integer, ForeignKey("mandoubiat.id"))
    
    mandoubia = relationship("Mandoubia")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200))
    national_id = Column(String(20), unique=True, index=True)
    position = Column(String(100))
    salary = Column(Integer)
    hire_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    mandoubia_id = Column(Integer, ForeignKey("mandoubiat.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    mandoubia = relationship("Mandoubia")
    user = relationship("User")

class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    code = Column(String(20), unique=True, index=True)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    type = Column(String(50))  # Primary, Secondary, etc.
    is_active = Column(Boolean, default=True)
    mandoubia_id = Column(Integer, ForeignKey("mandoubiat.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    
    mandoubia = relationship("Mandoubia")
    employee = relationship("Employee")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200))
    national_id = Column(String(20), unique=True, index=True)
    birth_date = Column(DateTime)
    gender = Column(String(10))  # Male, Female
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    grade = Column(String(20))
    section = Column(String(20))
    is_active = Column(Boolean, default=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    mandoubia_id = Column(Integer, ForeignKey("mandoubiat.id"))
    
    school = relationship("School")
    mandoubia = relationship("Mandoubia")

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    status = Column(Enum(AttendanceStatus))
    student_id = Column(Integer, ForeignKey("students.id"))
    school_id = Column(Integer, ForeignKey("schools.id"))
    
    student = relationship("Student")
    school = relationship("School")

class MovementType(str, enum.Enum):
    TRANSFER = "transfer"
    PROMOTION = "promotion"
    DEMOTION = "demotion"

class Movement(Base):
    __tablename__ = "movements"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(MovementType))
    date = Column(DateTime)
    from_school_id = Column(Integer, ForeignKey("schools.id"))
    to_school_id = Column(Integer, ForeignKey("schools.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    
    from_school = relationship("School", foreign_keys=[from_school_id])
    to_school = relationship("School", foreign_keys=[to_school_id])
    student = relationship("Student")

class InventoryCondition(str, enum.Enum):
    NEW = "new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    description = Column(Text)
    quantity = Column(Integer)
    condition = Column(Enum(InventoryCondition))
    acquisition_date = Column(DateTime)
    value = Column(Integer)
    is_active = Column(Boolean, default=True)
    mandoubia_id = Column(Integer, ForeignKey("mandoubiat.id"))
    
    mandoubia = relationship("Mandoubia")
