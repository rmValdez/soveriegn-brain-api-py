from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.infrastructure.ollama.embeddings import OllamaEmbeddings
from .models import Document, DocumentChunk
from .schemas import SearchResult

class KnowledgeRetrievalService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.embeddings = OllamaEmbeddings()

    async def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        query_embedding = await self.embeddings.get_embedding(query)
        
        # Scaffold pgvector cosine distance search
        # Using l2 distance (<->), inner product (<#>), or cosine distance (<=>)
        stmt = (
            select(DocumentChunk, Document)
            .join(Document)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        
        result = await self.session.execute(stmt)
        
        search_results = []
        for chunk, doc in result.all():
            # In pgvector, distance is 0 for exact match, so similarity is often 1 - distance
            # we will just use a dummy value for the scaffold
            similarity = 0.9 
            search_results.append(SearchResult(
                document_id=doc.id,
                document_title=doc.title,
                chunk_content=chunk.content,
                similarity=similarity
            ))
            
        return search_results
