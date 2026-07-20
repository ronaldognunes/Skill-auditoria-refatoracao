import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv opcional — usar variáveis de sistema diretamente

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-in-production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DATABASE_PATH = os.getenv("DATABASE_PATH", "loja.db")
