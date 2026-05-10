from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import DailyReport, User, UserRole, School, Mandoubia
from routes.auth import verify_token
from schemas import DailyReportCreate
from datetime import datetime

router = APIRouter()

@router.post("/daily-reports/")
async def submit_daily_report(
    report: DailyReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(verify_token)
):
    if user.role != UserRole.MODIR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only modir can submit daily reports")

    today_reports = (
        db.query(DailyReport)
        .filter(
            DailyReport.school_id == report.school_id,
            DailyReport.date == datetime.today().date()
        )
        .all()
    )

    if len(today_reports) > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A daily report for this school already exists today")

    new_report = DailyReport(
        school_id=report.school_id,
        date=datetime.today().date(),
        submitted_by=user.id,
        teachers_total=report.teachers_total,
        teachers_absent=report.teachers_absent,
        teachers_excused=report.teachers_excused,
        staff_total=report.staff_total,
        staff_absent=report.staff_absent,
        students_total=report.students_total,
        students_absent=report.students_absent,
        notes=report.notes
    )
    
    db.add(new_report)
    db.commit()
    return {"message": "Daily report submitted successfully"}

@router.get("/daily-reports/")
async def get_daily_reports(
    db: Session = Depends(get_db),
    user: User = Depends(verify_token)
):
    if user.role == UserRole.MANDOUB:
        reports = (
            db.query(DailyReport)
            .join(School, School.id == DailyReport.school_id)
            .filter(School.mandoubia_id == user.mandoubia_id)
            .all()
        )
    elif user.role == UserRole.MODIR:
        reports = (
            db.query(DailyReport)
            .filter(DailyReport.school_id == user.school_id)
            .all()
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to view daily reports")

    return [report.to_dict() for report in reports]

@router.get("/daily-reports/{school_id}/today")
async def get_todays_report(
    school_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(verify_token)
):
    if user.role == UserRole.MODIR and user.school_id != school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view reports for your own school")

    report = (
        db.query(DailyReport)
        .filter(
            DailyReport.school_id == school_id,
            DailyReport.date == datetime.today().date()
        )
        .first()
    )

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No daily report found for today")

    return report.to_dict()

@router.get("/daily-reports/missing-today")
async def get_missing_reports(
    db: Session = Depends(get_db),
    user: User = Depends(verify_token)
):
    if user.role != UserRole.MANDOUB:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only mandoub can view missing reports")

    schools_in_mandoubia = (
        db.query(School.id)
        .filter(School.mandoubia_id == user.mandoubia_id)
        .all()
    )

    submitted_schools_today = (
        db.query(DailyReport.school_id)
        .filter(
            DailyReport.date == datetime.today().date(),
            DailyReport.school_id.in_([school.id for school in schools_in_mandoubia])
        )
        .distinct()
        .all()
    )

    missing_reports = [
        {"id": school[0], "name": db.query(School.name).filter_by(id=school[0]).first()[0]}
        for school in schools_in_mandoubia
        if (school[0],) not in submitted_schools_today
    ]

    return missing_reports
