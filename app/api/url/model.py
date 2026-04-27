from datetime import timezone

from app.api.url.constants import SHORT_CODE_MAX_LENGTH
from app.extensions import db


class URLMapping(db.Model):
    __tablename__ = "url_mappings"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    short_code = db.Column(
        db.String(SHORT_CODE_MAX_LENGTH), unique=True, nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    access_count = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "shortCode": self.short_code,
            "createdAt": _serialize_datetime(self.created_at),
            "updatedAt": _serialize_datetime(self.updated_at),
            "accessCount": self.access_count,
        }


def _serialize_datetime(dt):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return (
        dt.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
