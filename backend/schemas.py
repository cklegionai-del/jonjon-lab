from pydantic import BaseModel, Field
from typing import Optional

class DailyReportCreate(BaseModel):
    teachers_total: int = Field(..., gt=0)
    teachers_absent: int = Field(..., ge=0)
    teachers_excused: int = Field(..., ge=0)
    staff_total: int = Field(..., gt=0)
    staff_absent: int = Field(..., ge=0)
    students_total: int = Field(..., gt=0)
    students_absent: int = Field(..., ge=0)
    notes: Optional[str] = None

class DailyReportResponse(BaseModel):
    id: int
    school_id: int
    date: str
    submitted_by: int
    teachers_total: int
    teachers_absent: int
    teachers_excused: int
    staff_total: int
    staff_absent: int
    students_total: int
    students_absent: int
    notes: Optional[str] = None
    status: str
    created_at: str

    class Config:
        orm_mode = True
