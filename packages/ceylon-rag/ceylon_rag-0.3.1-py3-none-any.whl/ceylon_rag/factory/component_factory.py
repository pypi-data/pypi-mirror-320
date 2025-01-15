from typing import Dict, Any

from ceylon_rag.interfaces.embedder import Embedder
from ceylon_rag.interfaces.llm import LLM
from ceylon_rag.interfaces.vector_store import VectorStore


class AsyncComponentFactory:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @staticmethod
    async def create_llm(type: str, **kwargs) -> LLM:
        if type == "ollama":
            from ceylon_rag.impl.llms.ollama import AsyncOllamaLLM
            return AsyncOllamaLLM(**kwargs)
        if type == "openai":
            from ceylon_rag.impl.llms.openai import AsyncOpenAILLM
            return AsyncOpenAILLM(**kwargs)
        raise ValueError(f"Unknown LLM type: {type}")

    @staticmethod
    async def create_embedder(type: str, **kwargs) -> Embedder:
        if type == "ollama":
            from ceylon_rag.impl.embedders.ollama_embedder import AsyncOllamaEmbedder
            return AsyncOllamaEmbedder(**kwargs)
        if type == "openai":
            from ceylon_rag.impl.embedders.openai_embedder import AsyncOpenAIEmbedder
            return AsyncOpenAIEmbedder(**kwargs)
        raise ValueError(f"Unknown embedder type: {type}")

    @staticmethod
    async def create_vector_store(type: str, embedder: Embedder, **kwargs) -> VectorStore:
        if type == "lancedb":
            from ceylon_rag.impl.vector_stores.lancedb_store import AsyncLanceDBStore
            return AsyncLanceDBStore(embedder=embedder, **kwargs)
        raise ValueError(f"Unknown vector store type: {type}")
