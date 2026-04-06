"""Core RAG pipeline: ingestion, retrieval, and generation."""
import os
import tempfile
import uuid
from pathlib import Path
from typing import AsyncIterator

import structlog
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document
from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.config import Settings
from app.rag.memory import get_memory

logger = structlog.get_logger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


class RAGPipeline:
    """Single-responsibility pipeline for document ingestion and RAG query."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

        self._embeddings = OllamaEmbeddings(
            model=settings.embedding_model,
            base_url=settings.ollama_base_url,
        )

        Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
        self._vectorstore = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=self._embeddings,
            persist_directory=settings.chroma_persist_dir,
        )

        self._llm = ChatOllama(
            model=settings.model_name,
            temperature=settings.temperature,
            base_url=settings.ollama_base_url,
            streaming=True,
        )

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

        logger.info("RAGPipeline initialised", model=settings.model_name)

    # ── Ingestion ──────────────────────────────────────────────────────────────

    def _load_document(self, file_path: str, original_filename: str) -> list[Document]:
        ext = Path(original_filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type '{ext}'. Supported: {SUPPORTED_EXTENSIONS}")

        loader_map = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".md": UnstructuredMarkdownLoader,
        }
        loader = loader_map[ext](file_path)
        return loader.load()

    def ingest(self, file_bytes: bytes, original_filename: str) -> int:
        """Ingest a document — returns number of chunks stored."""
        doc_id = str(uuid.uuid4())
        ext = Path(original_filename).suffix.lower()

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            raw_docs = self._load_document(tmp_path, original_filename)
            chunks = self._splitter.split_documents(raw_docs)

            # Enrich metadata
            for chunk in chunks:
                chunk.metadata["source_filename"] = original_filename
                chunk.metadata["doc_id"] = doc_id

            self._vectorstore.add_documents(chunks)
            logger.info("Documents ingested", filename=original_filename, chunks=len(chunks))
            return len(chunks)
        finally:
            os.unlink(tmp_path)

    # ── Query ──────────────────────────────────────────────────────────────────

    async def query(
        self,
        question: str,
        session_id: str,
    ) -> dict:
        """Run RAG query and return answer + source documents."""
        # Note: We are using a simplified version of the modern LCEL chain here.
        # For a full implementation including chat history, we normally use 
        # create_history_aware_retriever and create_retrieval_chain.
        
        # To keep it simple and compatible with existing logic:
        retriever = self._vectorstore.as_retriever(
            search_kwargs={"k": self._settings.retriever_k}
        )
        
        # Re-using the legacy chain for now as it's what was planned, 
        # but ensured the environment is fixed.
        chain = ConversationalRetrievalChain.from_llm(
            llm=self._llm,
            retriever=retriever,
            memory=get_memory(session_id),
            return_source_documents=True,
            verbose=False,
        )

        result = await chain.ainvoke({"question": question})
        return {
            "answer": result["answer"],
            "source_documents": result.get("source_documents", []),
        }

    # ── Document management ────────────────────────────────────────────────────

    def list_documents(self) -> list[dict]:
        """Return aggregated document metadata from the vector store."""
        collection = self._vectorstore._collection
        results = collection.get(include=["metadatas"])
        metadatas: list[dict] = results.get("metadatas") or []

        # Aggregate by doc_id
        docs: dict[str, dict] = {}
        for meta in metadatas:
            doc_id = meta.get("doc_id", "unknown")
            filename = meta.get("source_filename", "unknown")
            if doc_id not in docs:
                docs[doc_id] = {
                    "id": doc_id,
                    "filename": filename,
                    "source": meta.get("source", ""),
                    "chunk_count": 0,
                }
            docs[doc_id]["chunk_count"] += 1

        return list(docs.values())

    def delete_document(self, doc_id: str) -> int:
        """Delete all chunks for a given doc_id. Returns number deleted."""
        collection = self._vectorstore._collection
        results = collection.get(where={"doc_id": doc_id}, include=["metadatas"])
        ids = results.get("ids") or []
        if ids:
            collection.delete(ids=ids)
        logger.info("Document deleted", doc_id=doc_id, chunks_deleted=len(ids))
        return len(ids)
