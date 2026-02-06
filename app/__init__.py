"""
Flask Application Factory
"""
from flask import Flask, jsonify
from flask_cors import CORS
from app.core.config import get_config
from app.core.exceptions import VectorStoreError, ChatServiceError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app(config_name='development'):
    """
    Application factory pattern for creating Flask app instance.
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize CORS
    CORS(app, resources={
        r"/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    
    # Error handlers
    @app.errorhandler(VectorStoreError)
    def handle_vectorstore_error(error):
        logger.error(f"VectorStore error: {str(error)}")
        return jsonify({"error": str(error)}), 500
    
    @app.errorhandler(ChatServiceError)
    def handle_chat_service_error(error):
        logger.error(f"ChatService error: {str(error)}")
        return jsonify({"error": str(error)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500
    
    logger.info(f"Application initialized with {config_name} configuration")
    
    return app
