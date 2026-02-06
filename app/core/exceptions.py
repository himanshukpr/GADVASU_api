"""
Custom Exception Classes
"""


class VectorStoreError(Exception):
    """Raised when there's an error with the vector store operations"""
    pass


class ChatServiceError(Exception):
    """Raised when there's an error with the chat service"""
    pass


class DocumentLoadError(Exception):
    """Raised when documents cannot be loaded"""
    pass


class ValidationError(Exception):
    """Raised when request validation fails"""
    pass
