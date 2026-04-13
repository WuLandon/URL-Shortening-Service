import pytest


@pytest.fixture
def app(monkeypatch):
    # Ensure required config exists before app import/app factory execution.
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    from app import create_app

    flask_app = create_app("development")
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()
