import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_COUNTER_URL = os.getenv("REDIS_COUNTER_URL")
    REDIS_CACHE_URL = os.getenv("REDIS_CACHE_URL")
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    REDIS_COUNTER_URL = os.getenv("REDIS_COUNTER_URL")
    REDIS_CACHE_URL = os.getenv("REDIS_CACHE_URL")


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")
    REDIS_COUNTER_URL = (
        os.getenv("REDIS_COUNTER_URL")
        or os.getenv("TEST_REDIS_COUNTER_URL")
        or REDIS_URL
    )
    REDIS_CACHE_URL = (
        os.getenv("REDIS_CACHE_URL") or os.getenv("TEST_REDIS_CACHE_URL") or REDIS_URL
    )


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
