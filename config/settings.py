import os
from pathlib import Path
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

class Settings:
    # App Configuration
    APP_NAME = "AI File Generator"
    APP_VERSION = "3.0.0"
    ENVIRONMENT = Environment(os.getenv("ENVIRONMENT", "development"))
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    OUTPUT_DIR = BASE_DIR / "outputs"
    LOGS_DIR = BASE_DIR / "logs"
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    
    # AI Configuration - OpenRouter
    OR_API_KEY = os.getenv("OR_API_KEY", "")
    OR_MODEL = os.getenv("OR_MODEL", "mistralai/mistral-7b-instruct")
    
    # AI Configuration - HuggingFace
    HF_API_KEY = os.getenv("HF_API_KEY", "")
    HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    
    # AI Parameters
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "2048"))
    AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "30"))
    
    # File Generation
    PDF_PAGE_SIZE = "A4"
    PDF_MARGIN_INCHES = 0.5
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    
    # Validation
    MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "5000"))
    MIN_PROMPT_LENGTH = int(os.getenv("MIN_PROMPT_LENGTH", "10"))
    
    # Caching
    CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()