from flask import Blueprint, Response, jsonify, request

from app.api.url import controller

url_bp = Blueprint("url", __name__, url_prefix="/shorten")


@url_bp.route("", methods=["POST"])
def shorten_url():
    """Create a new shortened URL."""
    created_url = controller.create_short_url(request.get_json(silent=True) or {})
    return jsonify(created_url), 201


@url_bp.route("/<string:short_code>", methods=["GET"])
def get_shortened_url(short_code):
    """Retrieve details for a specific short code (stub)."""
    controller.get_short_url(short_code)
    return Response(status=501)


@url_bp.route("/<string:short_code>", methods=["PUT"])
def update_shortened_url(short_code):
    """Update an existing shortened URL (stub)."""
    controller.update_short_url(short_code, request.get_json(silent=True) or {})
    return Response(status=501)


@url_bp.route("/<string:short_code>", methods=["DELETE"])
def delete_shortened_url(short_code):
    """Delete an existing shortened URL (stub)."""
    controller.delete_short_url(short_code)
    return Response(status=501)


@url_bp.route("/<string:short_code>/stats", methods=["GET"])
def get_shortened_url_stats(short_code):
    """Retrieve usage stats for a specific short code (stub)."""
    controller.get_short_url_stats(short_code)
    return Response(status=501)
