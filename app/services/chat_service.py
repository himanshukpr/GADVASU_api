"""
Chat Service

Manages LangChain RAG pipeline and chat logic.
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.core.config import get_config
from app.core.constants import SYSTEM_PROMPT
from app.core.exceptions import ChatServiceError
from app.services.vector_service import VectorStoreService
from app.utils.helpers import format_documents
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChatService:
    """Service class for managing chat operations and RAG pipeline"""
    
    def __init__(self, config_name='development'):
        """Initialize the chat service"""
        self.config = get_config(config_name)()
        self.vector_service = VectorStoreService(config_name)
        self._chain = None
    
    def _create_llm(self) -> ChatOllama:
        """
        Create and configure the LLM instance.
        
        Returns:
            Configured ChatOllama instance
        """
        return ChatOllama(
            model=self.config.CHAT_MODEL,
            temperature=self.config.LLM_TEMPERATURE,
            num_ctx=self.config.LLM_NUM_CTX
        )
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create the chat prompt template.
        
        Returns:
            ChatPromptTemplate instance
        """
        return ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}")
        ])
    
    def _build_chain(self):
        """
        Build the RAG retrieval chain.
        
        Returns:
            Configured retrieval chain
        """
        try:
            logger.info("Building RAG chain...")
            
            # Get vectorstore and create retriever
            vectorstore = self.vector_service.get_vectorstore()
            retriever = vectorstore.as_retriever(
                search_kwargs={"k": self.config.RETRIEVER_K}
            )
            
            # Create LLM and prompt
            llm = self._create_llm()
            prompt = self._create_prompt()
            
            # Build the chain
            chain = (
                {
                    "context": retriever | RunnableLambda(format_documents),
                    "input": RunnablePassthrough(),
                }
                | prompt
                | llm
                | StrOutputParser()
            )
            
            logger.info("RAG chain built successfully")
            return chain
            
        except Exception as e:
            logger.error(f"Failed to build RAG chain: {str(e)}")
            raise ChatServiceError(f"Failed to build RAG chain: {str(e)}")
    
    def get_chain(self):
        """
        Get the retrieval chain (builds if not already built).
        
        Returns:
            Retrieval chain instance
        """
        if self._chain is None:
            self._chain = self._build_chain()
        return self._chain
    
    def chat(self, query: str) -> str:
        """
        Process a chat query and return the response.
        
        Args:
            query: User query string
        
        Returns:
            Chat response string
        
        Raises:
            ChatServiceError: If chat processing fails
        """
        try:
            logger.info(f"Processing query: {query[:50]}...")
            chain = self.get_chain()
            answer = chain.invoke(query)
            logger.info("Query processed successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Chat processing failed: {str(e)}")
            raise ChatServiceError(f"Chat processing failed: {str(e)}")
    
    def reset_chain(self) -> None:
        """Reset the chain (forces rebuild on next query)"""
        logger.info("Resetting chat chain")
        self._chain = None
