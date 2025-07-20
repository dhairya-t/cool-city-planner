"""
Application configuration settings
"""
import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    """Application settings"""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5001"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API Keys
    TWELVE_LABS_API_KEY: Optional[str] = os.getenv("TWELVE_LABS_API_KEY")
    VELLUM_API_KEY: Optional[str] = os.getenv("VELLUM_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    NASA_API_KEY: Optional[str] = os.getenv("NASA_API_KEY")
    
    # TwelveLabs Configuration
    TWELVE_LABS_BASE_URL: str = os.getenv("TWELVE_LABS_BASE_URL", "https://api.twelvelabs.io/v1.2")
    TWELVE_LABS_INDEX_ID: Optional[str] = os.getenv("TWELVE_LABS_INDEX_ID")
    
    # Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50000000"))  # 50MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # Timeout settings
    REQUEST_TIMEOUT: int = 300  # 5 minutes
    PROCESSING_TIMEOUT: int = 600  # 10 minutes
    
    class Config:
        case_sensitive = True

# Global settings instance
settings = Settings()
