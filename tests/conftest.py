import pytest


@pytest.fixture
def app(monkeypatch):
    """Ensure required config exists before app import/app factory execution."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    from app import create_app

    flask_app = create_app("development")
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_mock_url_mapping():
    """Factory for mock URL mapping objects with a to_dict() interface."""

    def _make_mock_url_mapping(**overrides):
        payload = {
            "id": 1,
            "url": "https://example.com",
            "shortCode": "abc123",
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-01T00:00:00Z",
            "accessCount": 0,
        }
        payload.update(overrides)

        class _MockUrlMapping:
            def to_dict(self):
                return payload

        return _MockUrlMapping()

    return _make_mock_url_mapping
