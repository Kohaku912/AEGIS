"""Capability retrieval index for lightweight LLM tool selection."""

from __future__ import annotations

import json
import logging
import math
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.capability_catalog import CapabilityCatalog

logger = logging.getLogger("aegis_ai.capability_index")

_TOKEN_RE = re.compile(r"[\w.-]+", re.UNICODE)
_EMBEDDING_DIM = 128


@dataclass
class CapabilityDocument:
    """Searchable representation of one capability manifest."""

    id: str
    short_name: str
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    server_id: str = ""
    app_id: str = ""
    action: str = ""
    risk_level: str = "low"
    input_parameter_names: list[str] = field(default_factory=list)
    examples: list[Any] = field(default_factory=list)

    @property
    def text(self) -> str:
        example_text = " ".join(_stringify_example(e) for e in self.examples)
        return " ".join(
            part
            for part in [
                self.id,
                self.short_name,
                self.title,
                self.description,
                " ".join(self.tags),
                " ".join(self.aliases),
                self.server_id,
                self.app_id,
                self.action,
                " ".join(self.input_parameter_names),
                example_text,
            ]
            if part
        )

    def to_lightweight_summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "tags": list(self.tags),
            "risk": self.risk_level,
            "short_desc": self.description[:220],
        }


@dataclass
class CapabilitySearchResult:
    document: CapabilityDocument
    combined_score: float = 0.0
    vector_score: float = 0.0
    keyword_score: float = 0.0
    tag_score: float = 0.0
    priority_score: float = 0.0


@dataclass
class CapabilitySelection:
    always_direct_tools: list[dict[str, Any]]
    retrieved_schema_tools: list[dict[str, Any]]
    lightweight_catalog: list[dict[str, Any]]
    all_candidate_ids: list[str]
    scores: dict[str, dict[str, float]]

    @property
    def tools(self) -> list[dict[str, Any]]:
        return [*self.always_direct_tools, *self.retrieved_schema_tools]


class _HashEmbeddingFunction:
    """Deterministic local embedding for Chroma without external downloads."""

    @staticmethod
    def name() -> str:
        """Return the stable Chroma embedding-function identifier."""

        return "aegis_hash_128"

    @staticmethod
    def build_from_config(config: dict[str, Any]) -> _HashEmbeddingFunction:
        """Recreate the stateless function from Chroma configuration."""

        del config
        return _HashEmbeddingFunction()

    def get_config(self) -> dict[str, Any]:
        """Return serializable Chroma configuration."""

        return {"dimension": _EMBEDDING_DIM}

    def __call__(self, input: list[str]) -> list[list[float]]:  # noqa: A002 - Chroma requires this name.
        return [_hash_embedding(text) for text in input]

    def embed_query(self, input: list[str]) -> list[list[float]]:  # noqa: A002 - Chroma protocol name.
        """Embed search queries using the same deterministic local transform."""
        return self(input)

    @staticmethod
    def is_legacy() -> bool:
        """Declare support for Chroma's current embedding-function protocol."""
        return False

    @staticmethod
    def default_space() -> str:
        """Return the distance space used by the normalized embeddings."""
        return "cosine"

    @staticmethod
    def supported_spaces() -> list[str]:
        """Return spaces supported by this embedding implementation."""
        return ["cosine", "l2", "ip"]


class CapabilityIndex:
    """Hybrid in-memory + Chroma index over capability manifests."""

    def __init__(
        self,
        catalog: CapabilityCatalog,
        *,
        chroma_path: str = "data/chroma/capabilities",
        collection_name: str = "aegis_capabilities",
        enable_chroma: bool = True,
    ) -> None:
        self._catalog = catalog
        self._chroma_path = chroma_path
        self._collection_name = collection_name
        self._enable_chroma = enable_chroma
        self._documents: dict[str, CapabilityDocument] = {}
        self._collection: Any = None
        self._lock = threading.RLock()
        self.reindex()

    def reindex(self) -> None:
        """Reload searchable documents from the current catalog state."""

        docs = {doc.id: doc for doc in (_document_from_manifest(manifest) for manifest in self._catalog.list_all())}
        with self._lock:
            self._documents = docs
            self._rebuild_chroma_locked()

    def get(self, capability_id: str) -> CapabilityDocument | None:
        with self._lock:
            return self._documents.get(capability_id)

    def all_documents(self) -> list[CapabilityDocument]:
        with self._lock:
            return list(self._documents.values())

    def search(
        self,
        query: str,
        *,
        top_k: int = 30,
        allowed_ids: set[str] | None = None,
    ) -> list[CapabilitySearchResult]:
        with self._lock:
            docs = [doc for doc in self._documents.values() if allowed_ids is None or doc.id in allowed_ids]
            vector_scores = self._vector_scores_locked(query, top_k=max(top_k * 3, top_k), allowed_ids=allowed_ids)

        results: list[CapabilitySearchResult] = []
        for doc in docs:
            vector_score = vector_scores.get(doc.id, 0.0)
            keyword_score = _keyword_score(query, doc)
            tag_score = _tag_score(query, doc)
            priority_score = _priority_score(doc)
            combined = 0.45 * vector_score + 0.35 * keyword_score + 0.10 * tag_score + 0.10 * priority_score
            results.append(
                CapabilitySearchResult(
                    document=doc,
                    combined_score=round(combined, 6),
                    vector_score=round(vector_score, 6),
                    keyword_score=round(keyword_score, 6),
                    tag_score=round(tag_score, 6),
                    priority_score=round(priority_score, 6),
                )
            )

        results.sort(key=lambda r: (r.combined_score, r.keyword_score, r.vector_score), reverse=True)
        return results[:top_k]

    def _rebuild_chroma_locked(self) -> None:
        self._collection = None
        if not self._enable_chroma:
            return
        try:
            import chromadb

            Path(self._chroma_path).mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=self._chroma_path)
            try:
                client.delete_collection(self._collection_name)
            except Exception:
                pass
            self._collection = client.get_or_create_collection(
                name=self._collection_name,
                embedding_function=_HashEmbeddingFunction(),
                metadata={"hnsw:space": "cosine"},
            )
            docs = list(self._documents.values())
            if docs:
                self._collection.upsert(
                    ids=[doc.id for doc in docs],
                    documents=[doc.text for doc in docs],
                    metadatas=[{"capability_id": doc.id} for doc in docs],
                )
        except Exception as exc:
            logger.warning("Capability Chroma index unavailable; using keyword fallback: %s", exc)
            self._collection = None

    def _vector_scores_locked(
        self,
        query: str,
        *,
        top_k: int,
        allowed_ids: set[str] | None = None,
    ) -> dict[str, float]:
        if self._collection is None or not query.strip():
            return {}
        try:
            count = self._collection.count()
            if count <= 0:
                return {}
            result = self._collection.query(
                query_texts=[query],
                n_results=min(max(top_k, 1), count),
                include=["distances", "metadatas"],
            )
            scores: dict[str, float] = {}
            ids = result.get("ids", [[]])[0] if result else []
            distances = result.get("distances", [[]])[0] if result else []
            for idx, cap_id in enumerate(ids):
                if allowed_ids is not None and cap_id not in allowed_ids:
                    continue
                distance = float(distances[idx]) if idx < len(distances) else 1.0
                scores[cap_id] = max(0.0, min(1.0, 1.0 - distance))
            return scores
        except Exception as exc:
            logger.warning("Capability vector search failed; using keyword fallback: %s", exc)
            return {}


class CapabilityRetriever:
    """Selects a small, relevant capability set for an LLM request."""

    def __init__(
        self,
        catalog: CapabilityCatalog,
        index: CapabilityIndex,
        *,
        always_direct_tool_names: set[str] | None = None,
    ) -> None:
        self._catalog = catalog
        self._index = index
        self._always_direct_tool_names = always_direct_tool_names or {
            "ask_user",
            "capability__search",
            "capability__describe",
        }

    def select_for_request(
        self,
        user_message: str,
        session_context: dict[str, Any] | None = None,
        top_k_schema: int = 8,
        top_k_summary: int = 30,
        allowed_ids: set[str] | None = None,
    ) -> CapabilitySelection:
        context = session_context or {}
        pinned_ids = _extract_context_ids(context)
        search_results = self._index.search(
            user_message,
            top_k=max(top_k_summary, top_k_schema),
            allowed_ids=allowed_ids,
        )

        ordered_ids: list[str] = []
        scores: dict[str, dict[str, float]] = {}
        for result in search_results:
            cap_id = result.document.id
            ordered_ids.append(cap_id)
            scores[cap_id] = {
                "combined": result.combined_score,
                "vector": result.vector_score,
                "keyword": result.keyword_score,
                "tag": result.tag_score,
                "priority": result.priority_score,
            }

        for cap_id in pinned_ids:
            if allowed_ids is not None and cap_id not in allowed_ids:
                continue
            if self._catalog.resolve(cap_id) and cap_id not in ordered_ids:
                ordered_ids.insert(0, cap_id)
                scores[cap_id] = {
                    "combined": 1.0,
                    "vector": 0.0,
                    "keyword": 0.0,
                    "tag": 0.0,
                    "priority": 1.0,
                }

        schema_ids = set(ordered_ids[:top_k_schema])
        summary_ids = ordered_ids[:top_k_summary]
        retrieved_schema_tools = self._catalog.list_for_tools(schema_ids) if schema_ids else []

        lightweight_catalog = []
        for cap_id in summary_ids:
            doc = self._index.get(cap_id)
            if doc is not None:
                lightweight_catalog.append(doc.to_lightweight_summary())

        return CapabilitySelection(
            always_direct_tools=build_always_direct_tools(),
            retrieved_schema_tools=retrieved_schema_tools,
            lightweight_catalog=lightweight_catalog,
            all_candidate_ids=summary_ids,
            scores=scores,
        )

    def search_lightweight(self, query: str, *, top_k: int = 10) -> list[dict[str, Any]]:
        return [
            {
                **result.document.to_lightweight_summary(),
                "score": result.combined_score,
            }
            for result in self._index.search(query, top_k=top_k)
        ]

    def describe(self, capability_id: str) -> dict[str, Any] | None:
        manifest = self._catalog.resolve(capability_id)
        if manifest is None:
            return None
        return {
            "id": manifest.capability_id,
            "short_name": manifest.short_name,
            "title": manifest.title,
            "description": manifest.description,
            "input_schema": manifest.input_schema or {"type": "object", "properties": {}},
            "examples": list(manifest.examples),
            "risk": manifest.risk_level,
            "notes": manifest.extra.get("notes", ""),
            "aliases": list(manifest.aliases),
            "tags": list(manifest.tags),
        }


def build_always_direct_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "ask_user",
                "description": "Ask the user a concise question when required information, confirmation, or manual completion is needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Question to show to the user."},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional short choices. Use an empty list for free text.",
                        },
                    },
                    "required": ["question"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "capability__search",
                "description": "Search available capabilities and return lightweight summaries. Use this when the visible catalog may not include the exact tool you need.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural language capability search query."},
                        "top_k": {
                            "type": "integer",
                            "description": "Maximum number of summaries to return.",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "capability__describe",
                "description": "Fetch detailed schema, examples, risk, and notes for one capability ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "capability_id": {"type": "string", "description": "Canonical capability ID to describe."},
                    },
                    "required": ["capability_id"],
                },
            },
        },
    ]


def _document_from_manifest(manifest: Any) -> CapabilityDocument:
    props = manifest.input_schema.get("properties", {}) if manifest.input_schema else {}
    return CapabilityDocument(
        id=manifest.capability_id,
        short_name=manifest.short_name,
        title=manifest.title,
        description=manifest.description,
        tags=list(manifest.tags),
        aliases=list(getattr(manifest, "aliases", [])),
        server_id=manifest.server_id,
        app_id=manifest.app_id,
        action=manifest.action,
        risk_level=manifest.risk_level,
        input_parameter_names=list(props.keys()),
        examples=list(getattr(manifest, "examples", [])),
    )


def _extract_context_ids(context: dict[str, Any]) -> list[str]:
    values: list[Any] = []
    for key in ("pinned_capability_ids", "recent_capability_ids", "session_capability_ids"):
        item = context.get(key)
        if isinstance(item, list):
            values.extend(item)
    result = []
    for value in values:
        if isinstance(value, str) and value not in result:
            result.append(value)
    return result


def _keyword_score(query: str, doc: CapabilityDocument) -> float:
    query_lower = query.lower()
    if not query_lower.strip():
        return 0.0

    weighted_fields = [
        (doc.id, 0.9),
        (doc.short_name, 0.8),
        (doc.title, 1.2),
        (doc.description, 0.9),
        (" ".join(doc.aliases), 1.6),
        (" ".join(doc.tags), 0.8),
        (" ".join(doc.input_parameter_names), 0.5),
        (" ".join(_stringify_example(e) for e in doc.examples), 0.7),
    ]
    score = 0.0
    max_score = sum(weight for text, weight in weighted_fields if text) or 1.0
    query_tokens = set(_tokens(query_lower))
    query_grams = set(_char_grams(query_lower))

    for text, weight in weighted_fields:
        if not text:
            continue
        text_lower = text.lower()
        field_score = 0.0
        if query_lower in text_lower or text_lower in query_lower:
            field_score = max(field_score, 1.0)
        field_tokens = set(_tokens(text_lower))
        if query_tokens and field_tokens:
            field_score = max(field_score, len(query_tokens & field_tokens) / len(query_tokens))
        field_grams = set(_char_grams(text_lower))
        if query_grams and field_grams:
            field_score = max(field_score, len(query_grams & field_grams) / len(query_grams))
        score += weight * field_score
    return max(0.0, min(1.0, score / max_score))


def _tag_score(query: str, doc: CapabilityDocument) -> float:
    query_tokens = set(_tokens(query.lower()))
    tags = {tag.lower() for tag in doc.tags}
    if not query_tokens or not tags:
        return 0.0
    return min(1.0, len(query_tokens & tags) / max(1, len(query_tokens)))


def _priority_score(doc: CapabilityDocument) -> float:
    # Do not hard-boost named capability ids — that biases autonomous choice.
    if doc.risk_level in ("low", "safe"):
        return 0.2
    return 0.0


def _tokens(text: str) -> list[str]:
    return [token for token in _TOKEN_RE.findall(text.lower()) if token]


def _char_grams(text: str) -> list[str]:
    compact = re.sub(r"\s+", "", text.lower())
    if len(compact) < 2:
        return []
    grams: list[str] = []
    for size in (2, 3):
        grams.extend(compact[i : i + size] for i in range(max(0, len(compact) - size + 1)))
    return grams


def _hash_embedding(text: str) -> list[float]:
    vector = [0.0] * _EMBEDDING_DIM
    features = _tokens(text) + _char_grams(text)
    for feature in features:
        idx = hash(feature) % _EMBEDDING_DIM
        vector[idx] += 1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _stringify_example(example: Any) -> str:
    if isinstance(example, str):
        return example
    try:
        return json.dumps(example, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(example)
