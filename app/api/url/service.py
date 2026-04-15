from sqlalchemy.exc import SQLAlchemyError

from app.api.url.model import URLMapping
from app.core.errors import NotFoundError
from app.core.utils import encode_base62
from app.extensions import db, redis_client


def create_short_url(url):
    """Create and persist a shortened URL mapping."""
    if redis_client is None:
        raise RuntimeError("Redis client is not configured.")

    count = redis_client.incr("global:url_counter")
    short_code = encode_base62(count)

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
