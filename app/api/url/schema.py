import re
from urllib.parse import urlparse

from app.api.url.constants import SHORT_CODE_MAX_LENGTH, SHORT_CODE_PREFIX
from app.core.errors import ValidationError

ALIAS_PATTERN = re.compile(r"^[a-z0-9_-]+$")


def _normalize_and_validate_url(raw_url):
    """Normalize and validate URL input."""
    if not isinstance(raw_url, str):
        raise ValidationError("Field 'url' is required and must be a string.")

    url = raw_url.strip()
    if not url:
        raise ValidationError("Field 'url' cannot be empty.")

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValidationError("Field 'url' must be a valid HTTP/HTTPS URL.")

    return url


def _normalize_and_validate_alias(raw_alias):
    """Normalize and validate alias input."""
    if not isinstance(raw_alias, str):
        raise ValidationError("Field 'alias' must be a string.")

    alias = raw_alias.strip().lower()
    if not alias:
        raise ValidationError("Field 'alias' cannot be empty.")

    if not ALIAS_PATTERN.fullmatch(alias):
        raise ValidationError(
            "Field 'alias' may contain only lowercase letters, numbers, '-' or '_'."
        )
    if len(alias) > SHORT_CODE_MAX_LENGTH:
        raise ValidationError(
            f"Field 'alias' must be at most {SHORT_CODE_MAX_LENGTH} characters."
        )
    if alias.startswith(SHORT_CODE_PREFIX):
        raise ValidationError(f"Field 'alias' cannot start with '{SHORT_CODE_PREFIX}'.")

    return alias


def validate_create_payload(payload):
    """Validate payload for creating a short URL."""
    if not isinstance(payload, dict):
        raise ValidationError("Invalid payload. Expected a JSON object.")

    validated_payload = {"url": _normalize_and_validate_url(payload.get("url"))}

    if "alias" in payload and payload.get("alias") is not None:
        validated_payload["alias"] = _normalize_and_validate_alias(payload.get("alias"))

    return validated_payload


def validate_update_payload(payload):
    """Validate payload for updating URL and/or alias."""
    if not isinstance(payload, dict):
        raise ValidationError("Invalid payload. Expected a JSON object.")

    validated_payload = {}

    if "url" in payload and payload.get("url") is not None:
        validated_payload["url"] = _normalize_and_validate_url(payload.get("url"))

    if "alias" in payload and payload.get("alias") is not None:
        validated_payload["alias"] = _normalize_and_validate_alias(payload.get("alias"))

    if not validated_payload:
        raise ValidationError("At least one of 'url' or 'alias' must be provided.")

    return validated_payload
