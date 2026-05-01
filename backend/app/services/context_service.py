from typing import Iterable, List


def normalize_keywords(values: Iterable[str]) -> List[str]:
    return [value.strip().lower() for value in values if value.strip()]


def city_match_score(observed_city: str, known_city: str) -> float:
    return 1.0 if observed_city.strip().lower() == known_city.strip().lower() else 0.0


def feature_overlap_score(observed_features: Iterable[str], known_features: Iterable[str]) -> float:
    observed_set = set(normalize_keywords(observed_features))
    known_set = set(normalize_keywords(known_features))
    if not observed_set or not known_set:
        return 0.0

    intersection = len(observed_set.intersection(known_set))
    union = len(observed_set.union(known_set))
    return intersection / union if union else 0.0


def combined_match_score(face_score: float, city_score: float, feature_score: float) -> float:
    weighted = (0.92 * face_score) + (0.05 * city_score) + (0.03 * feature_score)
    return min(max(weighted, 0.0), 1.0)


def build_match_reasons(face_score: float, city_score: float, feature_score: float) -> List[str]:
    reasons = [f"Face similarity: {round(face_score * 100, 2)}%"]

    if city_score > 0:
        reasons.append("Location context: observed city matches last known city")
    else:
        reasons.append("Location context: city differs from last known city")

    reasons.append(f"Feature overlap: {round(feature_score * 100, 2)}%")
    return reasons
