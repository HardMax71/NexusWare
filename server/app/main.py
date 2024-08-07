from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.database import engine, Base

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to NexusWare WMS API"}