import hashlib
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..database import (
    alerts_collection,
    matches_collection,
    missing_persons_collection,
    sightings_collection,
)
from ..config import settings
from ..models import utc_now
from ..services.context_service import (
    build_match_reasons,
    city_match_score,
    feature_overlap_score,
    normalize_keywords,
)
from ..services.email_service import send_match_alert
from ..services.face_service import detect_and_embed
from ..services.matching_service import as_percent, best_face_similarity, classify_similarity
from ..utils.file_storage import save_upload

router = APIRouter(prefix="/api/sightings", tags=["sightings"])


def file_sha256(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def is_exact_duplicate_sighting(person: dict, sighting_hash: str) -> bool:
    if not sighting_hash:
        return False

    known_hashes = [value for value in person.get("image_hashes", []) if value]
    if sighting_hash in known_hashes:
        return True

    for image_path in person.get("image_paths", []):
        if file_sha256(image_path) == sighting_hash:
            return True

    return False


def serialize_match(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "missing_person_id": str(doc["missing_person_id"]),
        "sighting_id": str(doc["sighting_id"]),
        "missing_person_name": doc.get("missing_person_name", ""),
        "confidence_percent": doc.get("confidence_percent", 0),
        "decision": doc.get("decision", "no_match"),
        "reasoning": doc.get("reasoning", []),
        "current_city": doc.get("current_city", ""),
        "description": doc.get("description", ""),
        "created_at": doc.get("created_at"),
        "user_feedback": doc.get("user_feedback"),
    }


def serialize_alert(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "match_id": str(doc["match_id"]),
        "to_email": doc.get("to_email", ""),
        "delivery_status": doc.get("delivery_status", "unknown"),
        "delivery_reason": doc.get("delivery_reason"),
        "created_at": doc.get("created_at"),
    }


@router.post("/report")
async def report_sighting(
    image: UploadFile = File(...),
    observed_features: str = Form(default=""),
    current_city: str = Form(...),
    description: str = Form(default=""),
) -> dict:
    saved_path = save_upload(image, category="sighting")
    sighting_hash = file_sha256(saved_path)

    try:
        query_embedding = detect_and_embed(saved_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    observed_feature_list = normalize_keywords(observed_features.split(","))

    sighting_doc = {
        "image_path": saved_path,
        "observed_features": observed_feature_list,
        "current_city": current_city.strip().lower(),
        "description": description.strip(),
        "created_at": utc_now(),
    }
    sighting_insert = sightings_collection.insert_one(sighting_doc)

    candidates = list(missing_persons_collection.find())
    if not candidates:
        return {
            "sighting_id": str(sighting_insert.inserted_id),
            "match": None,
            "message": "No registered missing persons yet.",
        }

    best_candidate = None
    best_rank_score = 0.0
    best_score_breakdown = {
        "face": 0.0,
        "city": 0.0,
        "features": 0.0,
    }

    for person in candidates:
        if is_exact_duplicate_sighting(person, sighting_hash):
            continue

        embeddings = person.get("embeddings", [])
        if not embeddings:
            continue

        face_score = best_face_similarity(query_embedding, embeddings)
        city_score = city_match_score(current_city, person.get("last_known_city", ""))
        feature_score = feature_overlap_score(
            observed_feature_list,
            person.get("physical_features", []),
        )

        # Rank mostly by face; context only breaks near ties.
        rank_score = (0.97 * face_score) + (0.02 * city_score) + (0.01 * feature_score)

        if rank_score > best_rank_score:
            best_candidate = person
            best_rank_score = rank_score
            best_score_breakdown = {
                "face": face_score,
                "city": city_score,
                "features": feature_score,
            }

    if not best_candidate:
        return {
            "sighting_id": str(sighting_insert.inserted_id),
            "match": None,
            "message": "No comparable face embeddings available. Upload a new sighting photo (not the same file as registration images).",
        }

    face_score = best_score_breakdown["face"]
    face_percent = as_percent(face_score)

    if face_score < settings.min_face_similarity_for_possible:
        return {
            "sighting_id": str(sighting_insert.inserted_id),
            "match": None,
            "message": "No confident match found.",
            "confidence_percent": face_percent,
            "face_similarity_percent": face_percent,
        }

    decision = classify_similarity(face_score)
    if decision == "strong_match" and face_score < settings.min_face_similarity_for_strong:
        decision = "possible_match"

    if decision == "no_match":
        return {
            "sighting_id": str(sighting_insert.inserted_id),
            "match": None,
            "message": "No confident match found.",
            "confidence_percent": face_percent,
            "face_similarity_percent": face_percent,
        }

    reasons = build_match_reasons(
        face_score=best_score_breakdown["face"],
        city_score=best_score_breakdown["city"],
        feature_score=best_score_breakdown["features"],
    )

    match_doc = {
        "missing_person_id": best_candidate["_id"],
        "sighting_id": sighting_insert.inserted_id,
        "missing_person_name": best_candidate["name"],
        "confidence_percent": face_percent,
        "decision": decision,
        "reasoning": reasons,
        "current_city": current_city.strip().lower(),
        "description": description.strip(),
        "sighting_image_path": saved_path,
        "user_feedback": None,
        "created_at": utc_now(),
    }
    match_insert = matches_collection.insert_one(match_doc)
    match_doc["_id"] = match_insert.inserted_id

    try:
        email_result = send_match_alert(
            to_email=best_candidate["reporter_email"],
            missing_person_name=best_candidate["name"],
            confidence_percent=match_doc["confidence_percent"],
            sighting_city=current_city,
            sighting_description=description,
            image_path=saved_path,
        )
    except Exception as exc:
        email_result = {
            "status": "failed",
            "reason": str(exc),
        }

    alert_doc = {
        "match_id": match_insert.inserted_id,
        "to_email": best_candidate["reporter_email"],
        "delivery_status": email_result.get("status", "unknown"),
        "delivery_reason": email_result.get("reason"),
        "created_at": utc_now(),
    }
    alert_insert = alerts_collection.insert_one(alert_doc)
    alert_doc["_id"] = alert_insert.inserted_id

    return {
        "sighting_id": str(sighting_insert.inserted_id),
        "match": serialize_match(match_doc),
        "alert": serialize_alert(alert_doc),
    }


@router.get("/matches")
def list_matches(limit: int = 50) -> list[dict]:
    limit = max(1, min(limit, 200))
    cursor = matches_collection.find().sort("created_at", -1).limit(limit)
    return [serialize_match(doc) for doc in cursor]


@router.get("/alerts")
def list_alerts(limit: int = 50) -> list[dict]:
    limit = max(1, min(limit, 200))
    cursor = alerts_collection.find().sort("created_at", -1).limit(limit)
    return [serialize_alert(doc) for doc in cursor]
