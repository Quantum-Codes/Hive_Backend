"""
RAG Verification Pipeline (Gemini + Chroma)

This module provides a Retrieval-Augmented Generation (RAG) pipeline that performs:
1) Vectorization and storage of documents in ChromaDB
2) Retrieval via vector similarity search
3) Answer generation and verification/classification using Google Gemini
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
import os
import json

from app.core.config import settings
from app.models.rag import RagRequest, RagResponse

import google.generativeai as genai
import chromadb
from chromadb.api.models.Collection import Collection


def _embed_texts_gemini(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts using Gemini embeddings API."""
    results: List[List[float]] = []
    for text in texts:
        if not text or not text.strip():
            results.append([])
            continue
        emb = genai.embed_content(model=settings.gemini.embed_model, content=text)
        # API returns {'embedding': [...]} as of current versions
        results.append(list(emb.get("embedding", [])))
    return results


class VerificationRAGPipeline:
    """
    Orchestrates retrieval, answer generation, and verification/classification.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        # Configure Gemini
        if settings.gemini.api_key:
            genai.configure(api_key=settings.gemini.api_key)
        self._model_name = model_name or settings.gemini.model
        self._temperature = temperature if temperature is not None else settings.gemini.temperature
        self._max_tokens = max_tokens if max_tokens is not None else settings.gemini.max_output_tokens
        self._llm = genai.GenerativeModel(self._model_name)

        # Setup ChromaDB (persistent)
        self._chroma_client = chromadb.PersistentClient(path=settings.vectordb.chroma_persist_path)
        self._collection: Collection = self._chroma_client.get_or_create_collection(
            name=settings.vectordb.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _build_corpus(self, contents: List[str], summary: Optional[str]) -> None:
        corpus: List[str] = []
        if summary:
            corpus.append(summary)
        corpus.extend(contents or [])
        # Deduplicate trivially
        dedup = list(dict.fromkeys([c for c in corpus if c and c.strip()]))
        if not dedup:
            return

        # Prepare IDs and embeddings
        ids = [f"doc_{i}" for i in range(len(dedup))]
        embeddings = _embed_texts_gemini(dedup)
        # Upsert into Chroma (replaces on duplicate IDs)
        self._collection.upsert(documents=dedup, embeddings=embeddings, ids=ids)

    def _retrieve(self, query: str, k: int = 4) -> List[str]:
        # Embed the query and search in Chroma
        q_emb = _embed_texts_gemini([query])[0]
        if not q_emb:
            return []
        result = self._collection.query(query_embeddings=[q_emb], n_results=max(1, k))
        # result["documents"] is List[List[str]]
        docs: List[str] = []
        if result and isinstance(result.get("documents"), list) and result["documents"]:
            docs = result["documents"][0]
        return docs

    def _generate_answer(self, query: str, context: List[str]) -> str:
        context_text = "\n\n".join(context) if context else ""
        prompt = (
            "You are a careful assistant. Use the provided context to answer the user's question. "
            "If the answer cannot be derived from the context, say you are unsure.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {query}\n\n"
            "Answer succinctly and cite specific context snippets."
        )
        resp = self._llm.generate_content(prompt)
        text = getattr(resp, "text", None)
        if not text and hasattr(resp, "candidates") and resp.candidates:
            # Fallback extraction
            try:
                text = resp.candidates[0].content.parts[0].text
            except Exception:
                text = ""
        return (text or "").strip()

    def _classify(self, query: str, answer: str, context: List[str]) -> Tuple[RagResponse, float, str]:
        """
        Ask the model to classify the verification outcome.

        Returns (label, confidence, rationale).
        """
        label_options = [e.value for e in RagResponse]
        context_text = "\n\n".join(context) if context else ""

        prompt = (
            "You are a fact verification assistant. Classify the claim based on the context and answer. "
            f"Choose one of: {', '.join(label_options)}.\n"
            "Return a JSON object with keys: label, confidence (0-1), rationale.\n"
            f"Claim: {query}\n"
            f"Answer: {answer}\n"
            f"Context: {context_text}"
        )
        resp = self._llm.generate_content(prompt)
        text = getattr(resp, "text", None)
        if not text and hasattr(resp, "candidates") and resp.candidates:
            try:
                text = resp.candidates[0].content.parts[0].text
            except Exception:
                text = ""
        resp_text = (text or "").strip()

        # Best-effort parse; fall back gracefully
        parsed_label: RagResponse = RagResponse.OTHER
        parsed_conf: float = 0.5
        rationale: str = resp_text

        try:
            data = json.loads(resp_text)
            label_str = str(data.get("label", "other")).lower()
            # Normalize to enum
            for e in RagResponse:
                if e.value.lower() == label_str:
                    parsed_label = e
                    break
            conf = float(data.get("confidence", 0.5))
            parsed_conf = max(0.0, min(1.0, conf))
            rationale = str(data.get("rationale", rationale))
        except Exception:
            # Keep defaults if parsing fails
            pass

        return parsed_label, parsed_conf, rationale

    def verify(self, request: RagRequest, top_k: int = 4) -> Dict[str, Any]:
        """
        Execute the RAG flow for a verification request.
        """
        if not request or not request.post_content:
            return {
                "status": RagResponse.UNVERIFIED.value,
                "reason": "No content provided for verification",
            }

        # Use the post content itself as the claim; build corpus from provided context + post content
        claim = request.post_content
        corpus_inputs = list(request.context or []) + [request.post_content]
        self._build_corpus(contents=corpus_inputs, summary=None)
        retrieved = self._retrieve(query=claim, k=top_k)
        answer = self._generate_answer(query=claim, context=retrieved)
        label, confidence, rationale = self._classify(claim, answer, retrieved)

        return {
            "status": label.value,
            "confidence": confidence,
            "answer": answer,
            "supporting_context": retrieved,
            "rationale": rationale,
            "metadata": {
                "post_id": request.post_id,
            },
        }


__all__ = ["VerificationRAGPipeline"]
