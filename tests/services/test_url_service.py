import pytest

from app.api.url.model import URLMapping
from app.api.url.service import (
    create_short_url,
    delete_short_url,
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
