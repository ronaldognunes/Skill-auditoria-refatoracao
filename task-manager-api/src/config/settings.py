import os

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-secret-change-in-production')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASS = os.getenv('SMTP_PASS', '')

JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
