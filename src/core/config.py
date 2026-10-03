import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "ScamShield AI")
    VERSION: str = os.getenv("VERSION", "1.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # OCR Settings
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    
    # Risk Fusion Configurable Weights
    WEIGHT_TEXT: float = float(os.getenv("WEIGHT_TEXT", "0.40"))
    WEIGHT_URL: float = float(os.getenv("WEIGHT_URL", "0.35"))
    WEIGHT_VISION: float = float(os.getenv("WEIGHT_VISION", "0.25"))
    CORRELATION_BOOST: float = float(os.getenv("CORRELATION_BOOST", "1.15"))
    
    # Risk Classification Thresholds
    THRESHOLD_LOW: float = 25.0
    THRESHOLD_MEDIUM: float = 50.0
    THRESHOLD_HIGH: float = 75.0

settings = Settings()
