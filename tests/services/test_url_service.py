import pytest

from app.api.url.model import URLMapping
from app.api.url.service import (
    create_short_url,
    delete_short_url,
    get_redirect_url,
    get_short_url,
    update_short_url,
)
from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.extensions import db


@pytest.fixture
def db_session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()


# ---------------------------------------------------------------------------
# create_short_url tests
# ---------------------------------------------------------------------------
def test_create_short_url_with_custom_alias(db_session):
    mapping = create_short_url("https://example.com", alias="my-alias")

    assert mapping.id is not None
    assert mapping.url == "https://example.com"
    assert mapping.short_code == "my-alias"
    assert mapping.access_count == 0


def test_create_short_url_rejects_duplicate_alias(db_session):
    create_short_url("https://example.com", alias="duplicate")

    with pytest.raises(ConflictError):
        create_short_url("https://another-example.com", alias="duplicate")


def test_create_short_url_rejects_case_insensitive_duplicate_alias(db_session):
    create_short_url("https://example.com", alias="MyAlias")

    with pytest.raises(ConflictError):
        create_short_url("https://another-example.com", alias="myalias")


def test_create_short_url_rejects_reserved_alias(db_session):
    with pytest.raises(ValidationError):
        create_short_url("https://example.com", alias="redirect")


# ---------------------------------------------------------------------------
# get_short_url tests
# ---------------------------------------------------------------------------
def test_get_short_url_returns_existing_mapping(db_session):
    created = create_short_url("https://example.com", alias="abc123")

    found = get_short_url("abc123")

    assert found.id == created.id
    assert found.url == "https://example.com"
    assert found.short_code == "abc123"


def test_get_short_url_raises_not_found_for_missing_code(db_session):
    with pytest.raises(NotFoundError):
        get_short_url("missing")


# ---------------------------------------------------------------------------
# update_short_url tests
# ---------------------------------------------------------------------------
def test_update_short_url_updates_url(db_session):
    create_short_url("https://example.com", alias="abc123")

    updated = update_short_url("abc123", {"url": "https://updated-example.com"})

    assert updated.url == "https://updated-example.com"
    assert updated.short_code == "abc123"


def test_update_short_url_updates_alias(db_session):
    create_short_url("https://example.com", alias="abc123")

    updated = update_short_url(
        "abc123", {"url": "https://example.com", "alias": "new-alias"}
    )

    assert updated.short_code == "new-alias"


def test_update_short_url_allows_same_alias_for_same_record(db_session):
    create_short_url("https://example.com", alias="abc123")

    updated = update_short_url(
        "abc123",
        {"url": "https://updated-example.com", "alias": "abc123"},
    )

    assert updated.url == "https://updated-example.com"
    assert updated.short_code == "abc123"


def test_update_short_url_rejects_alias_owned_by_another_record(db_session):
    create_short_url("https://example.com", alias="first")
    create_short_url("https://another-example.com", alias="second")

    with pytest.raises(ConflictError):
        update_short_url(
            "first",
            {"url": "https://example.com", "alias": "second"},
        )


def test_update_short_url_rejects_reserved_alias(db_session):
    create_short_url("https://example.com", alias="abc123")

    with pytest.raises(ValidationError):
        update_short_url(
            "abc123",
            {"url": "https://example.com", "alias": "redirect"},
        )


def test_update_short_url_raises_not_found_for_missing_code(db_session):
    with pytest.raises(NotFoundError):
        update_short_url("missing", {"url": "https://example.com"})


# ---------------------------------------------------------------------------
# delete_short_url tests
# ---------------------------------------------------------------------------
def test_delete_short_url_deletes_existing_mapping(db_session):
    create_short_url("https://example.com", alias="abc123")

    delete_short_url("abc123")

    deleted = URLMapping.query.filter_by(short_code="abc123").first()
    assert deleted is None


def test_delete_short_url_raises_not_found_for_missing_code(db_session):
    with pytest.raises(NotFoundError):
        delete_short_url("missing")


# ---------------------------------------------------------------------------
# get_redirect_url tests
# ---------------------------------------------------------------------------
def test_get_redirect_url_falls_back_to_db_when_cache_get_fails(
    db_session, monkeypatch
):
    create_short_url("https://example.com", alias="abc123")

    def raise_on_get(*args, **kwargs):
        raise RuntimeError("redis unavailable")

    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.get", raise_on_get
    )

    url = get_redirect_url("abc123")

    assert url == "https://example.com"


def test_get_redirect_url_returns_db_url_when_cache_set_fails(db_session, monkeypatch):
    create_short_url("https://example.com", alias="abc123")

    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.get", lambda *_: None
    )

    def raise_on_set(*args, **kwargs):
        raise RuntimeError("redis unavailable")

    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.set", raise_on_set
    )

    url = get_redirect_url("abc123")

    assert url == "https://example.com"


def test_get_redirect_url_caches_url_on_miss(db_session, monkeypatch):
    create_short_url("https://example.com", alias="abc123")
    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.get", lambda *_: None
    )

    calls = []

    def capture_set(key, value):
        calls.append((key, value))

    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.set", capture_set
    )

    url = get_redirect_url("abc123")

    assert url == "https://example.com"
    assert len(calls) == 1
    assert calls[0][1] == "https://example.com"


def test_get_redirect_url_cache_hit_raises_not_found_when_row_missing(
    db_session, monkeypatch
):
    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.get",
        lambda *_: "https://stale.com",
    )

    deleted_keys = []
    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.delete",
        lambda key: deleted_keys.append(key),
    )

    with pytest.raises(NotFoundError):
        get_redirect_url("missing")

    assert len(deleted_keys) == 1


def test_get_redirect_url_miss_path_raises_not_found_when_row_deleted_before_increment(
    db_session, monkeypatch
):
    create_short_url("https://example.com", alias="abc123")
    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.get", lambda *_: None
    )
    monkeypatch.setattr(
        "app.api.url.service_helpers.redis_cache_client.set", lambda *_: None
    )

    call_count = {"n": 0}

    original_increment = __import__(
        "app.api.url.service_helpers", fromlist=["_increment_access_count"]
    )._increment_access_count

    def deleting_increment(short_code):
        call_count["n"] += 1
        if call_count["n"] == 1:
            row = URLMapping.query.filter_by(short_code=short_code).first()
            db.session.delete(row)
            db.session.commit()
        return original_increment(short_code)

    monkeypatch.setattr(
        "app.api.url.service._increment_access_count",
        deleting_increment,
    )

    with pytest.raises(NotFoundError):
        get_redirect_url("abc123")
