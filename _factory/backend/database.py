from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pathlib import Path

# المسار المطلق لملف قاعدة البيانات
DB_PATH = Path(__file__).parent.parent / "data" / "factory.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    relative_path = Column(String)
    type = Column(String, nullable=False)
    category = Column(String, default="uncategorized")
    source = Column(String)
    size = Column(String)
    size_bytes = Column(Integer, default=0)
    extension = Column(String)
    files_count = Column(Integer, default=0)
    modified = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "path": self.path,
            "relativePath": self.relative_path, "type": self.type,
            "category": self.category, "source": self.source,
            "size": self.size, "sizeBytes": self.size_bytes,
            "extension": self.extension, "filesCount": self.files_count,
            "modified": self.modified.isoformat() if self.modified else None,
        }

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
