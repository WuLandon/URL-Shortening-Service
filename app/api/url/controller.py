from app.api.url import service
from app.api.url.schema import validate_payload


def create_short_url(payload):
    validated_payload = validate_payload(payload)

    created_mapping = service.create_short_url(validated_payload["url"])
    return created_mapping.to_dict()


def get_short_url(short_code):
    url_mapping = service.get_short_url(short_code)
    return url_mapping.to_dict()


def update_short_url(short_code, payload):
    validated_payload = validate_payload(payload)
    updated_mapping = service.update_short_url(short_code, validated_payload)
    return updated_mapping.to_dict()


def delete_short_url(short_code):
    """Handle deletion flow for a shortened URL."""
    service.delete_short_url(short_code)


def redirect_short_url(short_code):
    """Handle redirect flow for a short URL."""
    return service.get_redirect_url(short_code)
