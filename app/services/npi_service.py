import httpx
from app.config import settings
from app.models.schemas import PracticeInfo, Provider


# Mock data for demo when NPPES is unavailable or NPI not found
MOCK_PRACTICES: dict[str, dict] = {
    "1234567890": {
        "npi": "1234567890",
        "practice_name": "Springfield Family Medicine",
        "address": "742 Evergreen Terrace, Springfield, IL 62704",
        "specialty": "Family Medicine",
        "providers": [
            {"name": "Dr. Sarah Chen", "role": "Physician", "npi": "1234567890"},
            {"name": "Dr. James Patel", "role": "Physician", "npi": "1234567891"},
            {"name": "Lisa Monroe, NP", "role": "Nurse Practitioner", "npi": "1234567892"},
        ],
    },
    "9876543210": {
        "npi": "9876543210",
        "practice_name": "Bayview Cardiology Associates",
        "address": "1200 Harbor Blvd, Suite 300, San Francisco, CA 94107",
        "specialty": "Cardiology",
        "providers": [
            {"name": "Dr. Michael Torres", "role": "Physician", "npi": "9876543210"},
            {"name": "Dr. Aisha Rahman", "role": "Physician", "npi": "9876543211"},
        ],
    },
    "5551234567": {
        "npi": "5551234567",
        "practice_name": "Riverside Pediatrics",
        "address": "450 Main Street, Austin, TX 78701",
        "specialty": "Pediatrics",
        "providers": [
            {"name": "Dr. Emily Nguyen", "role": "Physician", "npi": "5551234567"},
            {"name": "Dr. Robert Kim", "role": "Physician", "npi": "5551234568"},
            {"name": "Maria Santos, PA", "role": "Physician Assistant", "npi": "5551234569"},
            {"name": "Jennifer Walsh, NP", "role": "Nurse Practitioner", "npi": "5551234570"},
        ],
    },
}


async def lookup_npi_live(npi: str) -> PracticeInfo | None:
    """Query the real NPPES registry API."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                settings.NPPES_BASE_URL,
                params={"version": "2.1", "number": npi, "limit": 1},
            )
            data = resp.json()

            if data.get("result_count", 0) == 0:
                return None

            result = data["results"][0]
            basic = result.get("basic", {})
            addr = result.get("addresses", [{}])[0]
            taxonomy = result.get("taxonomies", [{}])[0]

            org_name = basic.get("organization_name", "")
            if not org_name:
                first = basic.get("first_name", "")
                last = basic.get("last_name", "")
                org_name = f"Dr. {first} {last}" if first else "Unknown Practice"

            return PracticeInfo(
                npi=npi,
                practice_name=org_name,
                address=f"{addr.get('address_1', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('postal_code', '')[:5]}",
                specialty=taxonomy.get("desc", "General Practice"),
                providers=[
                    Provider(name=org_name, role=taxonomy.get("desc", "Provider"), npi=npi)
                ],
            )
    except Exception:
        return None


def lookup_npi_mock(npi: str) -> PracticeInfo | None:
    """Fallback to mock data for demo purposes."""
    if npi in MOCK_PRACTICES:
        data = MOCK_PRACTICES[npi]
        return PracticeInfo(
            npi=data["npi"],
            practice_name=data["practice_name"],
            address=data["address"],
            specialty=data["specialty"],
            providers=[Provider(**p) for p in data["providers"]],
        )
    return None


async def lookup_npi(npi: str) -> PracticeInfo | None:
    """Try live NPPES first, fall back to mock data."""
    result = await lookup_npi_live(npi)
    if result:
        return result
    return lookup_npi_mock(npi)
