from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.ollama.embeddings import OllamaEmbeddings
from .models import Document, DocumentChunk
from .schemas import DocumentCreate

class KnowledgeIngestionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.embeddings = OllamaEmbeddings()

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        # Basic chunking logic
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        return chunks

    async def ingest_document(self, doc_in: DocumentCreate) -> Document:
        # Create Document
        db_doc = Document(title=doc_in.title, source=doc_in.source)
        self.session.add(db_doc)
        await self.session.commit()
        
        # Chunk content
        chunks = self._chunk_text(doc_in.content)
        
        # Embed and save chunks
        for i, text_chunk in enumerate(chunks):
            embedding = await self.embeddings.get_embedding(text_chunk)
            db_chunk = DocumentChunk(
                document_id=db_doc.id,
                content=text_chunk,
                chunk_index=i,
                embedding=embedding
            )
            self.session.add(db_chunk)
            
        await self.session.commit()
        await self.session.refresh(db_doc)
        return db_doc
