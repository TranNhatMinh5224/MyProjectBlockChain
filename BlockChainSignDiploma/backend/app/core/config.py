"""
Application Configuration
Load settings from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== DATABASE ====================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "blockchain_diploma")

# Construct DATABASE_URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ==================== JWT ====================
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
ISSUER = os.getenv("ISSUER", "BlockChainDiploma")
AUDIENCE = os.getenv("AUDIENCE", "BlockChainDiploma")

# ==================== SMTP ====================
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_ENABLE_SSL = os.getenv("SMTP_ENABLE_SSL", "true").lower() == "true"
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "BlockChain Diploma System")

# ==================== APPLICATION ====================
APP_NAME = os.getenv("APP_NAME", "Blockchain Diploma Management System")
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ==================== LOGGING ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# ==================== PDF GENERATION ====================
PDF_TEMPLATE_PATH = os.getenv("PDF_TEMPLATE_PATH", "app/Services/PDFService/templates/diploma_template.html")
PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "outputs/diplomas")

# ==================== VERIFICATION ====================
VERIFY_BASE_URL = os.getenv("VERIFY_BASE_URL", "https://verify.edu.vn")