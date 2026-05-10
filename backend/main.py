from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth, daily_reports

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Educational Dashboard API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(daily_reports.router, prefix="/api", tags=["Daily Reports"])

@app.get("/")
async def root():
    return {"message": "Educational Dashboard API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
