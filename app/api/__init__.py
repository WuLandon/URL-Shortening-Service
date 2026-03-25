"""API package bootstrap and blueprint registration helpers."""

from app.api.routes import api_bp


def register_blueprints(app):
    """Register all top-level blueprints on the Flask app."""
    app.register_blueprint(api_bp, url_prefix="/api/v1")
