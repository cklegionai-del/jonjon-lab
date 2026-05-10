from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth
from models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tunisian Educational Administration System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to Tunisian Educational Administration System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
