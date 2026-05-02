import hashlib
from pathlib import Path
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Request
from ..schemas import MissingPersonCreate

from ..database import missing_persons_collection
from ..models import utc_now
from ..services.face_service import detect_and_embed
from ..utils.file_storage import save_upload

router = APIRouter(prefix="/api/missing-persons", tags=["missing-persons"])


def parse_feature_keywords(raw_features: str) -> List[str]:
    return [feature.strip().lower() for feature in raw_features.split(",") if feature.strip()]


def file_sha256(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def serialize_missing_person(doc: dict) -> dict:
    # Support both older field names and the test-friendly schema.
    result = {
        "id": str(doc.get("_id") or doc.get("id", "")),
        "name": doc.get("name"),
    }

    # Test-oriented fields
    for k in ["age", "gender", "city", "description", "phone", "email", "photos", "date_reported"]:
        if k in doc:
            result[k] = doc.get(k)

    # Legacy/internal fields
    if "last_known_city" in doc:
        result.setdefault("city", doc.get("last_known_city"))
    if "reporter_email" in doc:
        result.setdefault("email", doc.get("reporter_email"))
    if "image_paths" in doc:
        result.setdefault("photos", doc.get("image_paths"))

    result["created_at"] = doc.get("created_at")
    return result


@router.post("")
async def register_missing_person(
    request: Request,
    name: Optional[str] = Form(None),
    height_cm: Optional[float] = Form(default=None),
    physical_features: str = Form(default=""),
    last_known_city: Optional[str] = Form(None),
    reporter_email: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(default=None),
) -> dict:
    """Support both JSON-based creation (used by tests) and form/multipart
    creation which handles uploaded images and face embeddings.
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
        # Validate input against schema so tests receive 422 on invalid input
        try:
            person = MissingPersonCreate(**payload)
        except Exception as e:
            from pydantic import ValidationError

            if isinstance(e, ValidationError):
                raise HTTPException(status_code=422, detail=str(e)) from e
            raise

        document = person.model_dump()
        document["created_at"] = utc_now()
        insert_result = missing_persons_collection.insert_one(document)
        saved = missing_persons_collection.find_one({"_id": insert_result.inserted_id})
        return serialize_missing_person(saved)

    # Fallback to form-based processing (uploads + embeddings)
    if not images:
        raise HTTPException(status_code=400, detail="At least one image is required")

    image_paths: List[str] = []
    image_hashes: List[str] = []
    embeddings: List[List[float]] = []

    for image_file in images:
        saved_path = save_upload(image_file, category="missing")
        image_paths.append(saved_path)
        image_hashes.append(file_sha256(saved_path))
        try:
            embedding = detect_and_embed(saved_path)
            embeddings.append(embedding.tolist())
        except ValueError:
            continue
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not embeddings:
        raise HTTPException(
            status_code=400,
            detail="No detectable face found in provided images",
        )

    document = {
        "name": name.strip() if name else None,
        "height_cm": height_cm,
        "physical_features": parse_feature_keywords(physical_features),
        "last_known_city": (last_known_city or "").strip().lower(),
        "reporter_email": (reporter_email or "").strip().lower(),
        "image_paths": image_paths,
        "image_hashes": [value for value in image_hashes if value],
        "embeddings": embeddings,
        "created_at": utc_now(),
    }

    insert_result = missing_persons_collection.insert_one(document)
    saved = missing_persons_collection.find_one({"_id": insert_result.inserted_id})
    return serialize_missing_person(saved)


@router.put("/{person_id}")
def update_missing_person(person_id: str, payload: dict) -> dict:
    try:
        object_id = ObjectId(person_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid person id") from exc

    update_fields = {k: v for k, v in payload.items() if v is not None}
    missing_persons_collection.update_one({"_id": object_id}, {"$set": update_fields})
    updated = missing_persons_collection.find_one({"_id": object_id})
    if not updated:
        raise HTTPException(status_code=404, detail="Missing person not found")
    return serialize_missing_person(updated)


@router.delete("/{person_id}")
def delete_missing_person(person_id: str):
    try:
        object_id = ObjectId(person_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid person id") from exc

    res = missing_persons_collection.delete_one({"_id": object_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Missing person not found")
    return {"status": "deleted"}


@router.get("")
def list_missing_people() -> list[dict]:
    cursor = missing_persons_collection.find().sort("created_at", -1)
    return [serialize_missing_person(doc) for doc in cursor]


@router.get("/{person_id}")
def get_missing_person(person_id: str) -> dict:
    try:
        object_id = ObjectId(person_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid person id") from exc

    doc = missing_persons_collection.find_one({"_id": object_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Missing person not found")

    return serialize_missing_person(doc)
