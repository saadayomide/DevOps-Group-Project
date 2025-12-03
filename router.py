from fastapi import APIRouter, HTTPException
from models import CompareRequest, CompareResponse
from service import compare_items

router = APIRouter(prefix="/teamc", tags=["teamc"])


@router.post("/compare", response_model=CompareResponse)
async def teamc_compare(payload: CompareRequest):
    """
    TeamC compare endpoint (development helper).
    - Accepts items and optional stores.
    - Uses an in-memory price table (SAMPLE_PRICES) from service.py for now.
    """
    resp = compare_items(payload)
    if resp is None:
        raise HTTPException(status_code=400, detail="Compare failed")
    return resp
