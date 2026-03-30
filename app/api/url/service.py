from sqlalchemy.exc import SQLAlchemyError

from app.api.url.model import URLMapping
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
    """Fetch a shortened URL entity (business logic placeholder)."""
    return None


def update_short_url(short_code, payload):
    """Update a shortened URL entity (business logic placeholder)."""
    return None


def delete_short_url(short_code):
    """Delete a shortened URL entity (business logic placeholder)."""
    return None


def get_short_url_stats(short_code):
    """Fetch statistics for a shortened URL (business logic placeholder)."""
    return None
