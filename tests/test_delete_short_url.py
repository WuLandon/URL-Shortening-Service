def test_delete_shorten_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.url.service.delete_short_url",
        lambda short_code: None,
    )

    response = client.delete("/api/v1/shorten/abc123")

    assert response.status_code == 204
    assert response.data == b""


def test_delete_shorten_missing(client, monkeypatch):
    def _raise_not_found(short_code):
        from app.core.errors import NotFoundError

        raise NotFoundError(f"Short code '{short_code}' was not found.")

    monkeypatch.setattr("app.api.url.service.delete_short_url", _raise_not_found)

    response = client.delete("/api/v1/shorten/missing123")

    assert response.status_code == 404
    body = response.get_json()
    assert body is not None
    assert "error" in body
