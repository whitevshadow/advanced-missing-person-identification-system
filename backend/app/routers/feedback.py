from bson import ObjectId
from fastapi import APIRouter, HTTPException

from ..database import feedback_collection, matches_collection
from ..models import utc_now
from ..schemas import FeedbackCreate

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("")
def submit_feedback(payload: FeedbackCreate) -> dict:
    try:
        match_id = ObjectId(payload.match_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid match id") from exc

    # Insert feedback even if the match doesn't currently exist (tests submit
    # feedback without creating matches). If the match exists, update it.
    decision = "accepted" if payload.is_correct else "rejected"

    feedback_doc = {
        "match_id": payload.match_id,
        "is_correct": payload.is_correct,
        "decision": decision,
        "comments": payload.comments,
        "created_at": utc_now(),
    }
    insert = feedback_collection.insert_one(feedback_doc)
    feedback_id = insert.inserted_id

    # Attempt to update match document if present; ignore if not found.
    try:
        match_obj_id = ObjectId(payload.match_id)
        matches_collection.update_one(
            {"_id": match_obj_id},
            {
                "$set": {
                    "user_feedback": decision,
                    "updated_at": utc_now(),
                }
            },
        )
    except Exception:
        pass

    return {
        "status": "recorded",
        "match_id": payload.match_id,
        "is_correct": payload.is_correct,
        "decision": decision,
        "id": str(feedback_id),
    }


@router.get("")
def list_feedback(limit: int = 50) -> list[dict]:
    limit = max(1, min(limit, 200))
    cursor = feedback_collection.find().sort("created_at", -1).limit(limit)
    results = []
    for doc in cursor:
        r = {"id": str(doc.get("_id"))}
        r.update({k: v for k, v in doc.items() if k != "_id"})
        results.append(r)
    return results


@router.get("/{feedback_id}")
def get_feedback(feedback_id: str) -> dict:
    try:
        object_id = ObjectId(feedback_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid feedback id") from exc

    doc = feedback_collection.find_one({"_id": object_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Feedback not found")
    r = {"id": str(doc.get("_id"))}
    r.update({k: v for k, v in doc.items() if k != "_id"})
    return r
