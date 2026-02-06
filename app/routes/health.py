"""
Health Check Routes
"""
from flask import Blueprint, jsonify
from app.core.constants import MSG_HEALTH_OK

health_bp = Blueprint('health', __name__)


@health_bp.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with status
    """
    return jsonify({
        "status": "ok",
        "message": MSG_HEALTH_OK
    }), 200
