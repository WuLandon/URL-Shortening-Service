from datetime import datetime, timezone

from app.api.url.model import _serialize_datetime


def test_serialize_datetime_treats_naive_as_utc():
    naive = datetime(2026, 4, 27, 12, 34, 56, 123456)

    result = _serialize_datetime(naive)

    assert result == "2026-04-27T12:34:56Z"


def test_serialize_datetime_normalizes_aware_to_utc():
    aware = datetime(2026, 4, 27, 12, 34, 56, tzinfo=timezone.utc)

    result = _serialize_datetime(aware)

    assert result == "2026-04-27T12:34:56Z"
