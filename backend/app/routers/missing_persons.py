import hashlib
from pathlib import Path
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

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
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "height_cm": doc.get("height_cm"),
        "physical_features": doc.get("physical_features", []),
        "last_known_city": doc.get("last_known_city", ""),
        "reporter_email": doc.get("reporter_email", ""),
        "image_paths": doc.get("image_paths", []),
        "created_at": doc.get("created_at"),
    }


@router.post("")
async def register_missing_person(
    name: str = Form(...),
    height_cm: Optional[float] = Form(default=None),
    physical_features: str = Form(default=""),
    last_known_city: str = Form(...),
    reporter_email: str = Form(...),
    images: List[UploadFile] = File(...),
) -> dict:
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
        "name": name.strip(),
        "height_cm": height_cm,
        "physical_features": parse_feature_keywords(physical_features),
        "last_known_city": last_known_city.strip().lower(),
        "reporter_email": reporter_email.strip().lower(),
        "image_paths": image_paths,
        "image_hashes": [value for value in image_hashes if value],
        "embeddings": embeddings,
        "created_at": utc_now(),
    }

    insert_result = missing_persons_collection.insert_one(document)
    saved = missing_persons_collection.find_one({"_id": insert_result.inserted_id})
    return serialize_missing_person(saved)


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
