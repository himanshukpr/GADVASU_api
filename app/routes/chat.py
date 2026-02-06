"""
Chat and Vector Index Routes
"""
from flask import Blueprint, request, jsonify
from app.services.chat_service import ChatService
from app.services.vector_service import VectorStoreService
from app.core.constants import MSG_INDEX_REBUILT, MSG_QUERY_REQUIRED
from app.core.exceptions import ChatServiceError, VectorStoreError
from app.utils.helpers import validate_query
from app.utils.logger import setup_logger
import os

logger = setup_logger(__name__)

chat_bp = Blueprint('chat', __name__)

# Initialize services (singleton pattern)
_chat_service = None
_vector_service = None


def get_chat_service():
    """Get or create chat service instance"""
    global _chat_service
    if _chat_service is None:
        env = os.getenv('FLASK_ENV', 'development')
        _chat_service = ChatService(env)
    return _chat_service


def get_vector_service():
    """Get or create vector service instance"""
    global _vector_service
    if _vector_service is None:
        env = os.getenv('FLASK_ENV', 'development')
        _vector_service = VectorStoreService(env)
    return _vector_service


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for querying the dairy farming assistant.
    
    Request body:
        {
            "query": "your question here"
        }
    
    Returns:
        JSON response with answer
    """
    try:
        data = request.get_json(force=True)
        query = data.get('query', '').strip()
        
        # Validate query
        is_valid, error_msg = validate_query(query)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Process query
        chat_service = get_chat_service()
        answer = chat_service.chat(query)
        
        return jsonify({"answer": answer}), 200
        
    except ChatServiceError as e:
        logger.error(f"Chat service error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@chat_bp.route('/rebuild_index', methods=['POST'])
def rebuild_index():
    """
    Rebuild FAISS index from DOCX files in the data directory.
    
    Returns:
        JSON response confirming rebuild
    """
    try:
        logger.info("Received request to rebuild index")
        
        # Rebuild vectorstore
        vector_service = get_vector_service()
        vector_service.rebuild_vectorstore()
        
        # Reset chat service to use new index
        chat_service = get_chat_service()
        chat_service.reset_chain()
        
        logger.info("Index rebuild completed successfully")
        return jsonify({"message": MSG_INDEX_REBUILT}), 200
        
    except VectorStoreError as e:
        logger.error(f"Vector store error during rebuild: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error during index rebuild: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
