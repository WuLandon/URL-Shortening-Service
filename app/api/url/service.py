from flask import current_app
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

# TODO: Do I need separate constants.py file for SHORT_CODE_PREFIX?
from app.api.url.constants import SHORT_CODE_PREFIX
from app.api.url.model import URLMapping
from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.utils import encode_base62
from app.extensions import db, redis_client


def _is_alias_taken(alias):
    """Check whether alias already exists (case-insensitive)."""
    return (
        URLMapping.query.filter(
            func.lower(URLMapping.short_code) == alias.lower()
        ).first()
        is not None
    )


def _is_reserved_alias(alias):
    """Check whether alias conflicts with reserved keywords."""
    reserved_aliases = current_app.config.get("RESERVED_ALIASES", ())
    reserved_aliases_set = {value.lower() for value in reserved_aliases}
    return alias.lower() in reserved_aliases_set


def _generate_short_code():
    """Generate unique short code."""
    count = redis_client.incr("global:url_counter")
    short = f"{SHORT_CODE_PREFIX}{encode_base62(count)}"
    return short


def create_short_url(url, alias=None):
    """Create and persist a shortened URL mapping."""
    if redis_client is None:
        raise RuntimeError("Redis client is not configured.")

    if alias is not None:
        if alias.startswith(SHORT_CODE_PREFIX):
            raise ValidationError(f"Alias cannot start with '{SHORT_CODE_PREFIX}'.")
        if _is_reserved_alias(alias):
            raise ValidationError(
                f"'{alias}' is a reserved keyword and cannot be used as an alias."
            )
        if _is_alias_taken(alias):
            raise ConflictError(f"This alias '{alias}' already exists.")
        short_code = alias
    else:
        short_code = _generate_short_code()

    url_mapping = URLMapping(url=url, short_code=short_code)  # type: ignore

    try:
        db.session.add(url_mapping)
        db.session.commit()
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
    """Update the destination URL for an existing short link."""
    url_mapping = get_short_url(short_code)

    url_mapping.url = payload["url"]

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

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

    return None


def get_redirect_url(short_code):
    """Fetch original URL for redirect and increment access count."""
    url_mapping = get_short_url(short_code)
    url_mapping.increment_access()

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    return url_mapping.url
