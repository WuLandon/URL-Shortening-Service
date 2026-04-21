import re
from urllib.parse import urlparse

from app.api.url.constants import SHORT_CODE_PREFIX
from app.core.errors import ValidationError

ALIAS_PATTERN = re.compile(r"^[a-z0-9_-]+$")


# TODO: separate url validation from alias validation?
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

    validated_payload = {"url": url}

    if "alias" in payload and payload.get("alias") is not None:
        raw_alias = payload.get("alias")
        if not isinstance(raw_alias, str):
            raise ValidationError("Field 'alias' must be a string.")

        alias = raw_alias.strip().lower()
        if not alias:
            raise ValidationError("Field 'alias' cannot be empty.")

        if not ALIAS_PATTERN.fullmatch(alias):
            raise ValidationError(
                "Field 'alias' may contain only lowercase letters, numbers, '-' or '_'."
            )
        if alias.startswith(SHORT_CODE_PREFIX):
            raise ValidationError(
                f"Field 'alias' cannot start with '{SHORT_CODE_PREFIX}'."
            )

        validated_payload["alias"] = alias

    return validated_payload
