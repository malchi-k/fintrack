import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # Render использует postgres://, а SQLAlchemy 2+ требует postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Локальная разработка (SQLite)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
            os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'fintrack.db'
        )