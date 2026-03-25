"""Extension initialization module for shared third-party instances."""


class Database:
    """Minimal database extension placeholder for future ORM integration."""

    def init_app(self, app):
        """Attach database extension to the Flask app."""
        # Placeholder hook for SQLAlchemy (or equivalent) initialization.
        app.extensions["db"] = self


# Global extension instance used by the app factory.
db = Database()


def init_extensions(app):
    """Initialize all registered extension placeholders."""
    db.init_app(app)
