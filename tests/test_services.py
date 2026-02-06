"""
Service Layer Tests
"""
import pytest
from app.utils.helpers import validate_query, format_documents
from langchain_core.documents import Document


def test_validate_query_valid():
    """Test query validation with valid input"""
    is_valid, error = validate_query("What is mastitis?")
    assert is_valid is True
    assert error == ""


def test_validate_query_empty():
    """Test query validation with empty input"""
    is_valid, error = validate_query("")
    assert is_valid is False
    assert "empty" in error.lower()


def test_validate_query_whitespace():
    """Test query validation with whitespace only"""
    is_valid, error = validate_query("   ")
    assert is_valid is False
    assert "empty" in error.lower()


def test_validate_query_too_long():
    """Test query validation with too long input"""
    long_query = "a" * 1001
    is_valid, error = validate_query(long_query)
    assert is_valid is False
    assert "long" in error.lower()


def test_format_documents():
    """Test document formatting helper"""
    docs = [
        Document(page_content="First document"),
        Document(page_content="Second document"),
        Document(page_content="Third document")
    ]
    
    result = format_documents(docs)
    assert "First document" in result
    assert "Second document" in result
    assert "Third document" in result
    assert result.count("\n\n") == 2  # Two separators for three docs


def test_format_documents_empty():
    """Test document formatting with empty list"""
    result = format_documents([])
    assert result == ""
