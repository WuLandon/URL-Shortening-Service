"""Application configuration classes for different environments."""

import os


class BaseConfig:
    """Base configuration shared by all environments."""

    # Flask core settings.
    DEBUG = False
    TESTING = False

    # Placeholder database URL for future SQLAlchemy integration.
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///url_shortener.db")


class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG = True


class ProductionConfig(BaseConfig):
    """Configuration for production deployment."""

    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
