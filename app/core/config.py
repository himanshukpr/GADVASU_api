"""
Configuration Management
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Data paths
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    VECTOR_DIR = os.path.join(BASE_DIR, 'faiss_index')
    
    # AI Model settings
    CHAT_MODEL = os.getenv('CHAT_MODEL', 'llama3.2:1b')
    EMBED_MODEL = os.getenv('EMBED_MODEL', 'nomic-embed-text')
    
    # Ollama settings
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    # LangChain settings
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
    RETRIEVER_K = int(os.getenv('RETRIEVER_K', 4))
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', 0.0))
    LLM_NUM_CTX = int(os.getenv('LLM_NUM_CTX', 4096))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='development'):
    """Get configuration object by name"""
    return config_map.get(config_name, DevelopmentConfig)
