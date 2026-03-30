from app.api.url import service
from app.core.errors import ValidationError
from urllib.parse import urlparse


def create_short_url(payload):
    """Handle request data for creating a shortened URL."""
    if not isinstance(payload, dict):
        raise ValidationError("Invalid payload. Expected a JSON object.")

    raw_url = payload.get("url")
    if not isinstance(raw_url, str):
        raise ValidationError("Field 'url' is required and must be a string.")

    url = raw_url.strip()
    if not url:
        raise ValidationError("Field 'url' cannot be empty.")

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValidationError("Field 'url' must be a valid HTTP/HTTPS URL.")

    created_mapping = service.create_short_url(url)
    return created_mapping.to_dict()


def get_short_url(short_code):
    """Handle retrieval flow for a shortened URL record."""
    return None


def update_short_url(short_code, payload):
    """Handle update flow for an existing shortened URL."""
    return None


def delete_short_url(short_code):
    """Handle deletion flow for a shortened URL."""
    return None


def get_short_url_stats(short_code):
    """Handle retrieval flow for shortened URL analytics."""
    return None
