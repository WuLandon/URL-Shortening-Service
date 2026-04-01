"""Centralized custom error definitions and Flask error handlers."""

from flask import jsonify
from werkzeug.exceptions import BadRequest


class AppError(Exception):
    """Base application exception for controlled API errors."""

    status_code = 500

    def __init__(self, message="Application error", status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(AppError):
    """Raised when a requested resource cannot be found."""

    status_code = 404


class ValidationError(AppError):
    """Raised when request validation fails."""

    status_code = 400


def register_error_handlers(app):
    """Register global Flask error handlers for API responses."""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(BadRequest)
    def handle_bad_request(_error):
        return jsonify({"error": "Invalid JSON payload"}), 400

    @app.errorhandler(404)
    def handle_404(_error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_500(_error):
        return jsonify({"error": "Internal server error"}), 500
