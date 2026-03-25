"""Top-level API blueprint and nested route registration."""

from flask import Blueprint

from app.api.url.routes import url_bp

# Main API blueprint that groups feature-specific blueprints.
api_bp = Blueprint("api", __name__)

# Register URL shortening feature routes under /shorten.
api_bp.register_blueprint(url_bp)
