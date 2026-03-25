"""Local development entry point for running the Flask application."""

import os

from dotenv import load_dotenv

from app import create_app

# Load local environment variables from .env when present.
load_dotenv()

# Select runtime environment from environment variable.
config_name = os.getenv("FLASK_ENV", "development")
app = create_app(config_name=config_name)


if __name__ == "__main__":
    # Development-only runtime invocation.
    app.run(host="0.0.0.0", port=5000)
