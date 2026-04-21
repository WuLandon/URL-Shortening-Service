import pytest


@pytest.fixture
def stub_update_short_url(monkeypatch, make_mock_url_mapping):
    def _fake_update_short_url(short_code, payload):
        assert isinstance(short_code, str)
        assert isinstance(payload, dict)
        if "url" in payload:
            assert isinstance(payload["url"], str)
        if "alias" in payload:
            assert isinstance(payload["alias"], str)
        return make_mock_url_mapping(
            url=payload.get("url", "https://example.com"),
            shortCode=payload.get("alias", "abc123"),
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


def test_put_shorten_alias_only_success(client, stub_update_short_url):
    response = client.put(
        "/api/v1/shorten/abc123",
        json={"alias": "new-alias"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body["shortCode"] == "new-alias"
    assert body["url"] == "https://example.com"


def test_put_shorten_alias_is_normalized_to_lowercase(client, stub_update_short_url):
    response = client.put(
        "/api/v1/shorten/abc123",
        json={"alias": "My-NewAlias"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body["shortCode"] == "my-newalias"


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
        {"alias": ""},
        {"alias": "   "},
        {"alias": "_reserved"},
        {"alias": "bad alias"},
        {"alias": 123},
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


def test_put_shorten_duplicate_alias_returns_409(client, monkeypatch):
    from app.core.errors import ConflictError

    def _raise_duplicate_alias(short_code, payload):
        raise ConflictError(f"This alias '{payload['alias']}' already exists.")

    monkeypatch.setattr("app.api.url.service.update_short_url", _raise_duplicate_alias)

    response = client.put(
        "/api/v1/shorten/abc123",
        json={"alias": "existing_alias"},
    )

    assert response.status_code == 409
    body = response.get_json()
    assert body is not None
    assert "error" in body


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
