from app.api.url import service
from app.api.url.schema import validate_create_payload


def create_short_url(payload):
    """Handle request data for creating a shortened URL."""
    validated_payload = validate_create_payload(payload)

    created_mapping = service.create_short_url(validated_payload["url"])
    return created_mapping.to_dict()


def get_short_url(short_code):
    """Handle retrieval flow for a shortened URL record."""
    url_mapping = service.get_short_url(short_code)
    return url_mapping.to_dict()


def update_short_url(short_code, payload):
    """Handle update flow for an existing shortened URL."""
    return None


def delete_short_url(short_code):
    """Handle deletion flow for a shortened URL."""
    return None


def get_short_url_stats(short_code):
    """Handle retrieval flow for shortened URL analytics."""
    return None
