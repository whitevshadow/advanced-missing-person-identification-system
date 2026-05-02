from typing import Iterable, Sequence

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ..config import settings


def best_face_similarity(
    query_embedding: np.ndarray,
    registered_embeddings: Iterable[Sequence[float]],
) -> float:
    matrix = np.array(list(registered_embeddings), dtype=np.float32)
    if matrix.size == 0:
        return 0.0

    scores = cosine_similarity(query_embedding.reshape(1, -1), matrix)[0]
    max_score = float(np.max(scores))
    return float(np.clip(max_score, 0.0, 1.0))


def classify_similarity(score: float) -> str:
    if score >= settings.strong_match_threshold:
        return "strong_match"
    if score >= settings.possible_match_threshold:
        return "possible_match"
    return "no_match"


def as_percent(score: float) -> float:
    return round(score * 100, 2)


def calculate_similarity(emb1: Sequence[float], emb2: Sequence[float]) -> float:
    """Calculate cosine similarity between two embeddings and return a value in [0, 1].

    This is a small convenience wrapper used by tests and callers that expect
    a direct two-embedding API.
    """
    a = np.array(emb1, dtype=np.float32)
    b = np.array(emb2, dtype=np.float32)

    if a.size == 0 or b.size == 0:
        return 0.0

    # reshape to 2D for sklearn.cosine_similarity
    try:
        score = float(cosine_similarity(a.reshape(1, -1), b.reshape(1, -1))[0, 0])
    except Exception:
        # Fallback to manual computation if dimensions mismatch
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        score = float(np.dot(a, b) / denom)

    # Clip to [0,1]
    return float(np.clip(score, 0.0, 1.0))
