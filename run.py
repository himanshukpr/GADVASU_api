"""
Application Entry Point
"""
import os
from app import create_app
from app.utils.logger import setup_logger

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')

# Create Flask app
app = create_app(config_name)

# Setup logger
logger = setup_logger(__name__, app.config.get('LOG_FILE'))

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = config_name == 'development'
    
    logger.info(f"Starting application in {config_name} mode")
    logger.info(f"Server running on http://{host}:{port}")
    
    app.run(host=host, port=port, debug=debug)
