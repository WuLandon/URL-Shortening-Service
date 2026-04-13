def test_get_shorten_success(client, monkeypatch):
    class _MockUrlMapping:
        def to_dict(self):
            return {
                "id": 1,
                "url": "https://example.com",
                "shortCode": "abc123",
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
                "accessCount": 0,
            }

    monkeypatch.setattr(
        "app.api.url.service.get_short_url",
        lambda short_code: _MockUrlMapping(),
    )

    response = client.get("/api/v1/shorten/abc123")

    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body["shortCode"] == "abc123"
    assert body["url"] == "https://example.com"


def test_get_shorten_missing(client, monkeypatch):
    def _raise_not_found(short_code):
        from app.core.errors import NotFoundError

        raise NotFoundError(f"Short code '{short_code}' was not found.")

    monkeypatch.setattr("app.api.url.service.get_short_url", _raise_not_found)

    response = client.get("/api/v1/shorten/missing123")

    assert response.status_code == 404
    body = response.get_json()
    assert body is not None
    assert "error" in body
