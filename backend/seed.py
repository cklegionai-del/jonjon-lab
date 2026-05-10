from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, User, Mandoubia, School, UserRole, SchoolType
from routes.auth import get_password_hash
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://edu_user:edu_pass@postgres:5432/edu_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    db = SessionLocal()

    # Check if data already exists
    existing_mandoubia = db.query(Mandoubia).first()
    if existing_mandoubia:
        print("Data already seeded.")
        return

    # Create Mandoubia
    mandoubia_tun1 = Mandoubia(name="المندوبية الجهوية للتربية تونس 1", code="TUN1")
    db.add(mandoubia_tun1)
    
    # Create Schools
    primary_schools = [
        f"مدرسة ابتدائية {i}" for i in range(1, 97)
    ]
    secondary_schools = [
        f"المدرسة المتوسطة {i}" for i in range(1, 46)
    ]
    high_schools = [
        f"المدرسة الثانوية {i}" for i in range(1, 31)
    ]

    schools_addresses = ["Tunis Address " + str(i) for i in range(1, len(primary_schools) + len(secondary_schools) + len(high_schools) + 1)]

    all_schools = primary_schools + secondary_schools + high_schools

    for idx, school_name in enumerate(all_schools):
        school_type = SchoolType.PRIMARY if idx < len(primary_schools) else (SchoolType.SECONDARY if idx < len(primary_schools) + len(secondary_schools) else SchoolType.HIGH_SCHOOL)
        address = schools_addresses[idx]
        
        new_school = School(
            name=school_name,
            type=school_type,
            address=address,
            mandoubia_id=1
        )
        db.add(new_school)

    # Create Users
    admin_user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )

    mandoub_user = User(
        username="mandoub_tun1",
        email="mandoub_tun1@example.com",
        hashed_password=get_password_hash("pass123"),
        role=UserRole.SUPERVISOR,
        mandoubia_id=1
    )
    
    directors_users = [
        User(
            username=f"modir_{i}",
            email=f"modir{i}@example.com",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.DIRECTOR,
            school_id=i + 1
        ) for i in range(1, 4)
    ]

    db.add(admin_user)
    db.add(mandoub_user)
    db.add_all(directors_users)

    # Commit changes to the database
    db.commit()
    print("Data seeded successfully.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_data()
