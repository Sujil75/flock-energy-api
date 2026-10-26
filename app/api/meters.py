from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.clients.legacy_client import LegacyPortalClient
from app.schemas.meters import EnergyReading, MeterLocation
from app.schemas.normalizers import (
    normalize_energy_reading,
    normalize_location,
    normalize_meter_details,
    normalize_meter_list_item,
)

router = APIRouter(prefix="/api/v1/meters", tags=["Meters"])


def get_client() -> LegacyPortalClient:
    return LegacyPortalClient()


@router.get("")
def list_meters(
    q: str = Query(default="", description="Search meters"),
    page: int = Query(default=1, ge=1, description="Page number"),
) -> dict[str, Any]:
    try:
        client = get_client()
        result = client.get_meter_list(query=q, page=page)

        # Support either a direct list or a response containing "data".
        items = result if isinstance(result, list) else result.get("data", [])

        return {
            "data": [normalize_meter_list_item(item).model_dump() for item in items],
            "page": page,
            "query": q,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve meters from the legacy portal",
        ) from exc


@router.get("/{meter_id}")
def get_meter_details(meter_id: str) -> dict[str, Any]:
    try:
        client = get_client()
        result = client.get_meter_details(meter_id)
        return normalize_meter_details(result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve meter details from the legacy portal",
        ) from exc


@router.get("/{meter_id}/energy", response_model=list[EnergyReading])
def get_meter_energy(meter_id: str) -> list[EnergyReading]:
    try:
        client = get_client()
        result = client.get_meter_energy(meter_id)
        items = result.get("data", []) if isinstance(result, dict) else result

        return [normalize_energy_reading(item) for item in items]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve meter energy from the legacy portal",
        ) from exc


@router.get("/{meter_id}/location", response_model=MeterLocation)
def get_meter_location(meter_id: str) -> MeterLocation:
    try:
        client = get_client()
        result = client.get_meter_location(meter_id)
        return normalize_location(result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve meter location from the legacy portal",
        ) from exc
