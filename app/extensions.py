from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis


class RedisClient:
    def __init__(self, config_key):
        self._client = None
        self._config_key = config_key

    def init_app(self, app):
        redis_url = app.config.get(self._config_key)
        self._client = Redis.from_url(redis_url, decode_responses=True)

    def __getattr__(self, name):
        if self._client is None:
            raise RuntimeError(
                "Redis client is not initialized. Call init_extensions()."
            )
        return getattr(self._client, name)


db = SQLAlchemy()
migrate = Migrate()
redis_counter_client = RedisClient("REDIS_COUNTER_URL")
redis_cache_client = RedisClient("REDIS_CACHE_URL")


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    redis_counter_client.init_app(app)
    redis_cache_client.init_app(app)
