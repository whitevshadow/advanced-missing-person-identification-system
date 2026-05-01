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
