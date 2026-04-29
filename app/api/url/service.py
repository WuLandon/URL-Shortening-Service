from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.url.constants import RESERVED_ALIASES, SHORT_CODE_PREFIX, URL_CACHE_PREFIX
from app.api.url.model import URLMapping
from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.utils import encode_base62
from app.extensions import db, redis_cache_client, redis_counter_client


def _ensure_alias_unique(alias, current_id=None):
    """Alias must be unique, except for the record currently being updated."""
    existing = URLMapping.query.filter(
        func.lower(URLMapping.short_code) == alias.lower()
    ).first()

    if existing is not None and existing.id != current_id:
        raise ConflictError(f"This alias '{alias}' already exists.")


def _ensure_alias_not_reserved(alias):
    """Raise if alias conflicts with reserved keywords."""
    if alias.lower() in RESERVED_ALIASES:
        raise ValidationError(
            f"'{alias}' is a reserved keyword and cannot be used as an alias."
        )


def _generate_short_code():
    """Generate unique short code."""
    count = redis_counter_client.incr("global:url_counter")
    short = f"{SHORT_CODE_PREFIX}{encode_base62(count)}"
    return short


def _cache_key(short_code):
    return f"{URL_CACHE_PREFIX}{short_code}"


def create_short_url(url, alias=None):
    """Create and persist a shortened URL mapping."""
    if alias is not None:
        _ensure_alias_not_reserved(alias)
        _ensure_alias_unique(alias)
        short_code = alias
    else:
        short_code = _generate_short_code()

    url_mapping = URLMapping(url=url, short_code=short_code)  # type: ignore

    try:
        db.session.add(url_mapping)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        print(e.orig)
        raise ConflictError("A database constraint was violated.")
    except SQLAlchemyError:
        db.session.rollback()
        raise

    return url_mapping


def get_short_url(short_code):
    """Fetch a shortened URL entity."""
    url_mapping = URLMapping.query.filter_by(short_code=short_code).first()
    if url_mapping is None:
        raise NotFoundError(f"Short code '{short_code}' was not found.")
    return url_mapping


def update_short_url(short_code, payload):
    """Update the destination URL and/or alias for an existing short link."""
    url_mapping = get_short_url(short_code)
    old_short_code = url_mapping.short_code

    if "url" in payload:
        url_mapping.url = payload["url"]

    if "alias" in payload:
        alias = payload["alias"]
        _ensure_alias_not_reserved(alias)
        _ensure_alias_unique(alias, current_id=url_mapping.id)
        url_mapping.short_code = alias

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError("A database constraint was violated.")
    except SQLAlchemyError:
        db.session.rollback()
        raise

    redis_cache_client.delete(_cache_key(old_short_code))
    redis_cache_client.delete(_cache_key(url_mapping.short_code))

    return url_mapping


def delete_short_url(short_code):
    """Delete a shortened URL entity."""
    url_mapping = get_short_url(short_code)

    try:
        db.session.delete(url_mapping)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    redis_cache_client.delete(_cache_key(short_code))

    return None


def get_redirect_url(short_code):
    """Fetch original URL for redirect and increment access count."""
    cached_url = redis_cache_client.get(_cache_key(short_code))

    if cached_url is not None:
        _increment_access_count(short_code)
        return cached_url

    url = get_short_url(short_code).url
    redis_cache_client.set(_cache_key(short_code), url)
    _increment_access_count(short_code)

    return url


def _increment_access_count(short_code):
    try:
        db.session.query(URLMapping).filter_by(short_code=short_code).update(
            {URLMapping.access_count: URLMapping.access_count + 1},
            synchronize_session=False,
        )
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
