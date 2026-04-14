from urllib.parse import urlparse

from app.core.errors import ValidationError


def validate_payload(payload):
    """Validate url field from payload"""
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

    return {"url": url}
