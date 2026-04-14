import pytest


@pytest.fixture
def stub_update_short_url(monkeypatch, make_mock_url_mapping):
    def _fake_update_short_url(short_code, payload):
        assert isinstance(short_code, str)
        assert isinstance(payload, dict)
        assert isinstance(payload["url"], str)
        return make_mock_url_mapping(
            url="https://updated-example.com",
            shortCode="abc123",
            updatedAt="2026-01-02T00:00:00Z",
        )

    monkeypatch.setattr(
        "app.api.url.service.update_short_url",
        _fake_update_short_url,
    )


def test_put_shorten_success(client, stub_update_short_url):
    response = client.put(
        "/api/v1/shorten/abc123",
        json={"url": "https://updated-example.com"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body["shortCode"] == "abc123"
    assert body["url"] == "https://updated-example.com"


def test_put_shorten_missing(client, monkeypatch):
    def _raise_not_found(short_code, payload):
        from app.core.errors import NotFoundError

        raise NotFoundError(f"Short code '{short_code}' was not found.")

    monkeypatch.setattr("app.api.url.service.update_short_url", _raise_not_found)

    response = client.put(
        "/api/v1/shorten/missing123",
        json={"url": "https://updated-example.com"},
    )

    assert response.status_code == 404
    body = response.get_json()
    assert body is not None
    assert "error" in body


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"url": ""},
        {"url": "   "},
        {"url": 123},
        {"url": "not-a-valid-url"},
    ],
)
def test_put_shorten_invalid_payload(client, payload, stub_update_short_url):
    response = client.put("/api/v1/shorten/abc123", json=payload)

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert "error" in body
    assert isinstance(body["error"], str)
    assert body["error"]


def test_put_shorten_invalid_json(client, stub_update_short_url):
    response = client.put(
        "/api/v1/shorten/abc123",
        data='{"url": "https://updated-example.com"',
        content_type="application/json",
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert body["error"] == "Invalid JSON payload"
