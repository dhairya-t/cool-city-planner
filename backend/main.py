"""
CoolCity Planner FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.routes import router

# Setup logging
setup_logging("INFO" if settings.DEBUG else "WARNING")
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CoolCity Planner API",
    description="AI-powered urban heat island analysis using TwelveLabs, Vellum, and Google Gemini",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# Serve static files (for uploaded images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CoolCity Planner API is running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "coolcity-planner-api",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "twelve_labs_configured": bool(settings.TWELVE_LABS_API_KEY),
        "vellum_configured": bool(settings.VELLUM_API_KEY),
        "gemini_configured": bool(settings.GEMINI_API_KEY)
    }

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting CoolCity Planner API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Check API key configuration
    if not settings.TWELVE_LABS_API_KEY:
        logger.warning("TwelveLabs API key not configured - using mock data")
    if not settings.VELLUM_API_KEY:
        logger.warning("Vellum API key not configured")
    if not settings.GEMINI_API_KEY:
        logger.warning("Gemini API key not configured")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down CoolCity Planner API")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
