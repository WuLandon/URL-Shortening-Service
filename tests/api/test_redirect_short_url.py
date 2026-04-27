def test_redirect_short_url_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.url.service.get_redirect_url",
        lambda short_code: "https://example.com",
    )

    response = client.get("/api/v1/shorten/abc123/redirect", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == "https://example.com"


def test_redirect_short_url_missing(client, monkeypatch):
    def _raise_not_found(short_code):
        from app.core.errors import NotFoundError

        raise NotFoundError(f"Short code '{short_code}' was not found.")

    monkeypatch.setattr("app.api.url.service.get_redirect_url", _raise_not_found)

    response = client.get("/api/v1/shorten/missing123/redirect")

    assert response.status_code == 404
    body = response.get_json()
    assert body is not None
    assert "error" in body
