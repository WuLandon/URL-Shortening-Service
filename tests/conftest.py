import pytest


@pytest.fixture
def app(monkeypatch):
    from app import create_app

    flask_app = create_app("testing")
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
