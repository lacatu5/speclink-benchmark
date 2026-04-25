import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
PORT = int(os.environ.get("PORT", 8015))
HOST = os.environ.get("HOST", "0.0.0.0")
TOKEN_EXPIRY_HOURS = 24
MAX_TASKS_PER_USER = 100
