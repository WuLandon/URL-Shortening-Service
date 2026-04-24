import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL")
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
