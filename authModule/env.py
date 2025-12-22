import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class EnvConfig:
    # FOr the flask secret key
    
    DEBUG = True
    SECRET_KEY = "your_secret_key"

    # JWT keys :
    JWT_SECRET = "supersecret"
    JWT_REFRESH_SECRET = "refreshsecret"

    # PostgreSQL  URL
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:1234@localhost:5432/localstoragedb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # RSA Keys
    KEYS_DIR = os.path.join(BASE_DIR, "keys")
    PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "public_2025.pem")
    PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "private_2025.pem")

    # CORS
    FRONTEND_ORIGIN = "http://localhost:5173"
