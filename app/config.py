import os


class BaseConfig:
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL")
    # TODO: is this the best way to store/retrieve RESERVED_ALIASES
    RESERVED_ALIASES = tuple(
        alias.strip().lower()
        for alias in os.getenv(
            "RESERVED_ALIASES",
            "api,shorten,redirect,stats,admin,health,docs",
        ).split(",")
        if alias.strip()
    )

    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
