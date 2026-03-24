from fastapi import APIRouter, HTTPException
from app.models.schemas import PracticeInfo
from app.services.npi_service import lookup_npi

router = APIRouter(prefix="/api/npi", tags=["NPI"])

DEMO_NPIS = "1234567890, 9876543210, 5551234567"


@router.get("/{npi}", response_model=PracticeInfo)
async def npi_lookup(npi: str):
    """Look up a practice by NPI number via NPPES registry (with mock fallback)."""
    if not npi.isdigit() or len(npi) != 10:
        raise HTTPException(status_code=400, detail="NPI must be a 10-digit number.")

    result = await lookup_npi(npi)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"NPI not found. For demo, try: {DEMO_NPIS}",
        )
    return result
