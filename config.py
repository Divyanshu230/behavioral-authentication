import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))

    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    DATABASE_PATH = os.path.join(INSTANCE_DIR, "auth.db")

    DEBUG = True

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    BEHAVIOR_CONFIDENCE_THRESHOLD = 0.75

    @staticmethod
    def init_app(app):
        os.makedirs(Config.INSTANCE_DIR, exist_ok=True)