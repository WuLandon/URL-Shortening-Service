from typing import Optional

from flask import Flask

from app.api import register_blueprints
from app.config import config_by_name
from app.core.errors import register_error_handlers
from app.extensions import init_extensions


def create_app(config_name: Optional[str] = None) -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)

    selected_config = (config_name or "development").lower()
    if selected_config not in config_by_name:
        raise ValueError(
            f"Unknown config '{selected_config}'. Use development or production."
        )
    app.config.from_object(config_by_name[selected_config])

    init_extensions(app)

    # Register API blueprints.
    register_blueprints(app)

    # Register centralized error handlers.
    register_error_handlers(app)

    return app
