from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.url.model import URLMapping
from app.api.url.service_helpers import (
    _cache_key,
    _ensure_alias_not_reserved,
    _ensure_alias_unique,
    _generate_short_code,
    _increment_access_count,
    _safe_cache_delete,
)
from app.core.errors import ConflictError, NotFoundError
from app.extensions import db, redis_cache_client


def create_short_url(url, alias=None):
    """Create, persist, and return a new URLMapping model instance."""
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
    except IntegrityError:
        db.session.rollback()
        raise ConflictError("A database constraint was violated.")
    except SQLAlchemyError:
        db.session.rollback()
        raise

    return url_mapping


def get_short_url(short_code):
    """Return the URLMapping for `short_code` or raise NotFoundError."""
    url_mapping = URLMapping.query.filter_by(short_code=short_code).first()
    if url_mapping is None:
        raise NotFoundError(f"Short code '{short_code}' was not found.")
    return url_mapping


def update_short_url(short_code, payload):
    """Update an existing URLMapping and return the updated model instance."""
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

    _safe_cache_delete(old_short_code)
    _safe_cache_delete(url_mapping.short_code)

    return url_mapping


def delete_short_url(short_code):
    """Delete the URLMapping for `short_code` and invalidate related cache entries."""
    url_mapping = get_short_url(short_code)

    try:
        db.session.delete(url_mapping)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    _safe_cache_delete(short_code)

    return None


def get_redirect_url(short_code):
    """Resolve `short_code`, increment access statistics, and return the target URL."""
    try:
        cached_url = redis_cache_client.get(_cache_key(short_code))
    except Exception:
        cached_url = None

    if cached_url is not None:
        updated_rows = _increment_access_count(short_code)
        if updated_rows == 0:
            _safe_cache_delete(short_code)
            raise NotFoundError(f"Short code '{short_code}' was not found.")
        return cached_url

    url = get_short_url(short_code).url
    try:
        redis_cache_client.set(_cache_key(short_code), url)
    except Exception:
        pass
    updated_rows = _increment_access_count(short_code)
    if updated_rows == 0:
        _safe_cache_delete(short_code)
        raise NotFoundError(f"Short code '{short_code}' was not found.")

    return url
