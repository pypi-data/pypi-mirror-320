from abc import ABC, abstractmethod
from typing import List

from ceylon_rag.interfaces.schemas import Document


class Embedder(ABC):

    @abstractmethod
    async def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        """Embed a list of documents"""
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Embed a single query"""
        pass
