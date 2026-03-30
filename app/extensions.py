from redis import Redis
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


class RedisClient:
    def __init__(self):
        self._client = None

    def init_app(self, app):
        redis_url = app.config.get("REDIS_URL")
        self._client = Redis.from_url(redis_url, decode_responses=True)

    def __getattr__(self, name):
        if self._client is None:
            raise RuntimeError(
                "Redis client is not initialized. Call init_extensions()."
            )
        return getattr(self._client, name)


db = SQLAlchemy()
migrate = Migrate()
redis_client = RedisClient()


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    redis_client.init_app(app)
