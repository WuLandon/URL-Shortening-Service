import logging

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.api.url.constants import RESERVED_ALIASES, SHORT_CODE_PREFIX, URL_CACHE_PREFIX
from app.api.url.model import URLMapping
from app.core.errors import ConflictError, ValidationError
from app.extensions import db, redis_cache_client, redis_counter_client

logger = logging.getLogger(__name__)
BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode_base62(number):
    """Encode a non-negative integer as a Base62 string."""
    if not isinstance(number, int):
        raise TypeError("number must be an integer")

    if number < 0:
        raise ValueError("number must be non-negative")

    if number == 0:
        return BASE62_ALPHABET[0]

    encoded = []
    while number > 0:
        number, remainder = divmod(number, len(BASE62_ALPHABET))
        encoded.append(BASE62_ALPHABET[remainder])

    return "".join(reversed(encoded))


def _ensure_alias_unique(alias, current_id=None):
    """Raise ConflictError if alias is already used by another URLMapping."""
    existing = URLMapping.query.filter(
        func.lower(URLMapping.short_code) == alias.lower()
    ).first()

    if existing is not None and existing.id != current_id:
        raise ConflictError(f"This alias '{alias}' already exists.")


def _ensure_alias_not_reserved(alias):
    """Raise ValidationError if alias conflicts with a reserved keyword."""
    if alias.lower() in RESERVED_ALIASES:
        raise ValidationError(
            f"'{alias}' is a reserved keyword and cannot be used as an alias."
        )


def _generate_short_code():
    """Generate a unique system short code from the Redis atomic counter."""
    count = redis_counter_client.incr("global:url_counter")
    short = f"{SHORT_CODE_PREFIX}{encode_base62(count)}"
    return short


def _cache_key(short_code):
    """Return the Redis cache key for a short code."""
    return f"{URL_CACHE_PREFIX}{short_code}"


def _safe_cache_delete(short_code):
    """Delete a short code from the URL cache without failing the request."""
    try:
        redis_cache_client.delete(_cache_key(short_code))
    except Exception:
        logger.warning(
            "Cache delete failed for short_code=%s",
            short_code,
            exc_info=True,
        )


def _increment_access_count(short_code):
    """Atomically increment access_count for a short code. Return updated row count."""
    try:
        updated_rows = (
            db.session.query(URLMapping)
            .filter_by(short_code=short_code)
            .update(
                {URLMapping.access_count: URLMapping.access_count + 1},
                synchronize_session=False,
            )
        )
        db.session.commit()
        return updated_rows
    except SQLAlchemyError:
        db.session.rollback()
        raise
