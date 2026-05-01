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

    match_doc = matches_collection.find_one({"_id": match_id})
    if not match_doc:
        raise HTTPException(status_code=404, detail="Match not found")

    decision = "accepted" if payload.accepted else "rejected"

    feedback_doc = {
        "match_id": match_id,
        "accepted": payload.accepted,
        "decision": decision,
        "comments": payload.comments,
        "created_at": utc_now(),
    }
    feedback_collection.insert_one(feedback_doc)

    matches_collection.update_one(
        {"_id": match_id},
        {
            "$set": {
                "user_feedback": decision,
                "updated_at": utc_now(),
            }
        },
    )

    return {
        "status": "recorded",
        "match_id": payload.match_id,
        "decision": decision,
    }
