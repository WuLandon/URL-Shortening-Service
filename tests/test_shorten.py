import pytest


@pytest.fixture
def stub_create_short_url(monkeypatch):
    class _MockUrlMapping:
        def to_dict(self):
            return {
                "id": 1,
                "url": "https://example.com",
                "shortCode": "b",
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
                "accessCount": 0,
            }

    def _fake_create_short_url(url):
        assert isinstance(url, str)
        return _MockUrlMapping()

    monkeypatch.setattr(
        "app.api.url.service.create_short_url",
        _fake_create_short_url,
    )


def test_post_shorten_success(client, stub_create_short_url):
    # A valid URL payload should return 201 with resource fields.
    response = client.post("/api/v1/shorten", json={"url": "https://example.com"})

    assert response.status_code == 201
    body = response.get_json()
    assert body is not None
    assert body["url"] == "https://example.com"
    assert "id" in body
    assert "shortCode" in body
    assert "createdAt" in body
    assert "updatedAt" in body
    assert "accessCount" in body


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
def test_post_shorten_invalid_payload(client, payload, stub_create_short_url):
    # Missing/empty/invalid url values should return a validation error.
    response = client.post("/api/v1/shorten", json=payload)

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert "error" in body
    assert isinstance(body["error"], str)
    assert body["error"]


def test_post_shorten_invalid_json(client, stub_create_short_url):
    # Malformed JSON syntax should be handled as a 400 Bad Request.
    response = client.post(
        "/api/v1/shorten",
        data='{"url": "https://example.com"',
        content_type="application/json",
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert body["error"] == "Invalid JSON payload"
