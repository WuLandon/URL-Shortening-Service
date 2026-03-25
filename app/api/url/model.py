"""Data model placeholders for URL shortening domain entities."""


class URLMapping:
    """Placeholder entity for a shortened URL mapping."""

    def __init__(self, original_url=None, short_code=None):
        self.original_url = original_url
        self.short_code = short_code


class URLStats:
    """Placeholder entity for shortened URL statistics."""

    def __init__(self, short_code=None, access_count=0):
        self.short_code = short_code
        self.access_count = access_count
