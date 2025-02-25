import os
from dotenv import load_dotenv
load_dotenv()
# load_dotenv('.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = os.getenv('SMTP_HOST')
    MAIL_PORT = os.getenv('SMTP_PORT')
    MAIL_USE_TLS = os.getenv('SMTP_TLS')
    MAIL_USERNAME = os.getenv('SMTP_USER')
    MAIL_PASSWORD = os.getenv('SMTP_PASS')
    APP_NAME = os.getenv('APP_NAME')
    LOGS_PATH = os.getenv('LOGS_PATH')