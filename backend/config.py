import os
from datetime import timedelta

class Config:
    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'complain_box.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = "complainbox-super-secret-key-2024"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # Mail (configure with your SMTP — Gmail example)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")   # set in .env
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")   # set in .env
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "noreply@complainbox.com")

    # App
    SECRET_KEY = "flask-secret-key-complainbox"
    DEBUG = True
