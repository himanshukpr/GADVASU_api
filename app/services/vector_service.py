"""
Vector Store Service

Handles FAISS vectorstore creation, loading, and management.
"""
import os
from typing import List
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

from app.core.config import get_config
from app.core.exceptions import VectorStoreError, DocumentLoadError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VectorStoreService:
    """Service class for managing FAISS vectorstore operations"""
    
    def __init__(self, config_name='development'):
        """Initialize the vector store service"""
        self.config = get_config(config_name)()
        self.embeddings = OllamaEmbeddings(model=self.config.EMBED_MODEL)
        self._vectorstore = None
    
    def _load_documents(self) -> List:
        """
        Load all DOCX documents from the data directory.
        
        Returns:
            List of loaded documents
        
        Raises:
            DocumentLoadError: If no documents can be loaded
        """
        all_docs = []
        
        if not os.path.exists(self.config.DATA_DIR):
            raise DocumentLoadError(f"Data directory not found: {self.config.DATA_DIR}")
        
        doc_files = [f for f in os.listdir(self.config.DATA_DIR) 
                     if f.endswith(('.docx', '.doc'))]
        
        if not doc_files:
            raise DocumentLoadError("No DOCX files found in data directory")
        
        for filename in doc_files:
            path = os.path.join(self.config.DATA_DIR, filename)
            try:
                logger.info(f"Loading document: {filename}")
                loader = Docx2txtLoader(path)
                all_docs.extend(loader.load())
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
                raise DocumentLoadError(f"Failed to load {filename}: {str(e)}")
        
        if not all_docs:
            raise DocumentLoadError("No documents could be loaded")
        
        logger.info(f"Successfully loaded {len(all_docs)} document(s)")
        return all_docs
    
    def _split_documents(self, docs: List) -> List:
        """
        Split documents into chunks.
        
        Args:
            docs: List of documents to split
        
        Returns:
            List of document chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
        splits = text_splitter.split_documents(docs)
        logger.info(f"Split documents into {len(splits)} chunks")
        return splits
    
    def build_vectorstore(self) -> FAISS:
        """
        Build a new FAISS vectorstore from documents.
        
        Returns:
            FAISS vectorstore instance
        
        Raises:
            VectorStoreError: If vectorstore creation fails
        """
        try:
            logger.info("Building new vectorstore...")
            
            # Load and split documents
            docs = self._load_documents()
            splits = self._split_documents(docs)
            
            # Create vectorstore
            vectorstore = FAISS.from_documents(splits, self.embeddings)
            
            # Save to disk
            vectorstore.save_local(self.config.VECTOR_DIR)
            logger.info(f"Vectorstore saved to {self.config.VECTOR_DIR}")
            
            self._vectorstore = vectorstore
            return vectorstore
            
        except (DocumentLoadError, Exception) as e:
            logger.error(f"Failed to build vectorstore: {str(e)}")
            raise VectorStoreError(f"Failed to build vectorstore: {str(e)}")
    
    def load_vectorstore(self) -> FAISS:
        """
        Load existing FAISS vectorstore from disk.
        
        Returns:
            FAISS vectorstore instance
        
        Raises:
            VectorStoreError: If loading fails
        """
        try:
            if not os.path.exists(self.config.VECTOR_DIR):
                logger.warning("Vectorstore not found, building new one...")
                return self.build_vectorstore()
            
            logger.info(f"Loading vectorstore from {self.config.VECTOR_DIR}")
            vectorstore = FAISS.load_local(
                self.config.VECTOR_DIR,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            self._vectorstore = vectorstore
            logger.info("Vectorstore loaded successfully")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Failed to load vectorstore: {str(e)}")
            raise VectorStoreError(f"Failed to load vectorstore: {str(e)}")
    
    def get_vectorstore(self) -> FAISS:
        """
        Get the vectorstore instance (loads if not already loaded).
        
        Returns:
            FAISS vectorstore instance
        """
        if self._vectorstore is None:
            return self.load_vectorstore()
        return self._vectorstore
    
    def rebuild_vectorstore(self) -> None:
        """
        Rebuild the vectorstore from scratch.
        
        Raises:
            VectorStoreError: If rebuild fails
        """
        logger.info("Rebuilding vectorstore...")
        self._vectorstore = None
        self.build_vectorstore()
