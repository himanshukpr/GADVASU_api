"""
Helper Utilities
"""
from typing import List
from langchain_core.documents import Document


def format_documents(docs: List[Document]) -> str:
    """
    Format a list of LangChain documents into a single string.
    
    Args:
        docs: List of Document objects
    
    Returns:
        Formatted string with document contents
    """
    return "\n\n".join(doc.page_content for doc in docs)


def validate_query(query: str) -> tuple[bool, str]:
    """
    Validate user query.
    
    Args:
        query: User input query string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query) > 1000:
        return False, "Query too long (max 1000 characters)"
    
    return True, ""
