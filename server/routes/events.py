from typing import Optional

from fastapi import APIRouter

from utils.external.firestore import EventTable

router = APIRouter(prefix="/server")

@router.get("/events")
async def get_events(id: Optional[int] = None):
    if id:
        return EventTable.get_event_by_id(id)
    else:
        return EventTable.get_events()
