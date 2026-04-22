from app.api.url.constants import SHORT_CODE_MAX_LENGTH
from app.extensions import db


class URLMapping(db.Model):
    __tablename__ = "url_mappings"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    short_code = db.Column(
        db.String(SHORT_CODE_MAX_LENGTH), unique=True, nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        onupdate=db.func.now(),
    )
    access_count = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "shortCode": self.short_code,
            "createdAt": self.created_at.isoformat() + "Z",
            "updatedAt": self.updated_at.isoformat() + "Z",
            "accessCount": self.access_count,
        }
