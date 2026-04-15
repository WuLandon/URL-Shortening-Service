def test_get_shorten_stats_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.url.service.get_short_url_stats",
        lambda short_code: {
            "shortCode": short_code,
            "url": "https://example.com",
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-02T00:00:00Z",
            "accessCount": 7,
        },
    )

    response = client.get("/api/v1/shorten/abc123/stats")

    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body["shortCode"] == "abc123"
    assert body["accessCount"] == 7
    assert body["url"] == "https://example.com"


def test_get_shorten_stats_missing(client, monkeypatch):
    def _raise_not_found(short_code):
        from app.core.errors import NotFoundError

        raise NotFoundError(f"Short code '{short_code}' was not found.")

    monkeypatch.setattr("app.api.url.service.get_short_url_stats", _raise_not_found)

    response = client.get("/api/v1/shorten/missing123/stats")

    assert response.status_code == 404
    body = response.get_json()
    assert body is not None
    assert "error" in body
