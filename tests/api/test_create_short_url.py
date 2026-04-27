import pytest


@pytest.fixture
def stub_create_short_url(monkeypatch, make_mock_url_mapping):
    def _fake_create_short_url(url, alias=None):
        assert isinstance(url, str)
        short_code = alias if alias is not None else "_b"
        return make_mock_url_mapping(shortCode=short_code)

    monkeypatch.setattr(
        "app.api.url.service.create_short_url",
        _fake_create_short_url,
    )


def test_post_shorten_success(client, stub_create_short_url):
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
    response = client.post("/api/v1/shorten", json=payload)

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert "error" in body
    assert isinstance(body["error"], str)
    assert body["error"]


def test_post_shorten_invalid_json(client, stub_create_short_url):
    response = client.post(
        "/api/v1/shorten",
        data='{"url": "https://example.com"',
        content_type="application/json",
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert body["error"] == "Invalid JSON payload"


def test_post_shorten_custom_alias_is_normalized_to_lowercase(
    client, stub_create_short_url
):
    response = client.post(
        "/api/v1/shorten",
        json={"url": "https://example.com", "alias": "My_Custom-Alias"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body is not None
    assert body["shortCode"] == "my_custom-alias"


@pytest.mark.parametrize(
    "alias",
    [
        "",
        "   ",
        "_reserved",
        "bad alias",
        "bad/alias",
        "bad.alias",
    ],
)
def test_post_shorten_invalid_alias_payload(client, alias, stub_create_short_url):
    response = client.post(
        "/api/v1/shorten",
        json={"url": "https://example.com", "alias": alias},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert "error" in body


def test_post_shorten_reserved_alias_returns_400(client, monkeypatch):
    from app.core.errors import ValidationError

    def _raise_reserved_alias(url, alias=None):
        raise ValidationError(f"Alias '{alias}' is reserved and cannot be used.")

    monkeypatch.setattr("app.api.url.service.create_short_url", _raise_reserved_alias)

    response = client.post(
        "/api/v1/shorten",
        json={"url": "https://example.com", "alias": "redirect"},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert "error" in body


def test_post_shorten_duplicate_alias_returns_409(client, monkeypatch):
    from app.core.errors import ConflictError

    def _raise_duplicate_alias(url, alias=None):
        raise ConflictError(f"Alias '{alias}' already exists.")

    monkeypatch.setattr("app.api.url.service.create_short_url", _raise_duplicate_alias)

    response = client.post(
        "/api/v1/shorten",
        json={"url": "https://example.com", "alias": "existing_alias"},
    )

    assert response.status_code == 409
    body = response.get_json()
    assert body is not None
    assert "error" in body


def test_post_shorten_alias_too_long_returns_400(client, stub_create_short_url):
    response = client.post(
        "/api/v1/shorten",
        json={"url": "https://example.com", "alias": "a" * 17},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert body["error"] == "Field 'alias' must be at most 16 characters."
