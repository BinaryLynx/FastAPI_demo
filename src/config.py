from dotenv import load_dotenv
import os

load_dotenv()

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_LOGIN = os.environ.get("SMTP_LOGIN")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
DB_URI = os.environ.get("DB_URI")
