from flask import Blueprint, Response, jsonify, redirect, request

from app.api.url import controller

url_bp = Blueprint("url", __name__, url_prefix="/shorten")


@url_bp.route("", methods=["POST"])
def shorten_url():
    """Create a new shortened URL."""
    payload = request.get_json(silent=False)
    created_url = controller.create_short_url(payload)
    return jsonify(created_url), 201


@url_bp.route("/<string:short_code>", methods=["GET"])
def get_shortened_url(short_code):
    """Retrieve details for a specific short code."""
    url_details = controller.get_short_url(short_code)
    return jsonify(url_details), 200


@url_bp.route("/<string:short_code>", methods=["PUT"])
def update_shortened_url(short_code):
    """Update an existing shortened URL."""
    payload = request.get_json(silent=False)
    updated_url = controller.update_short_url(short_code, payload)
    return jsonify(updated_url), 200


@url_bp.route("/<string:short_code>", methods=["DELETE"])
def delete_shortened_url(short_code):
    """Delete an existing shortened URL."""
    controller.delete_short_url(short_code)
    return Response(status=204)


@url_bp.route("/<string:short_code>/redirect", methods=["GET"])
def redirect_shortened_url(short_code):
    """Redirect to the original URL for a specific short code."""
    target_url = controller.redirect_short_url(short_code)
    return redirect(target_url)
