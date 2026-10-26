import json
from typing import Any

from app.schemas.meters import (
    EnergyReading,
    MeterLocation,
    MeterResponse,
)


def normalize_meter_list_item(item: dict[str, Any]) -> MeterResponse:
    return MeterResponse(
        meter_id=str(item["meterId"]),
        serial_number=item.get("serialNo"),
        make=item.get("make"),
        phase_type=item.get("phaseType"),
        installation_status=item.get("installStatus"),
        dt_code=item.get("dtCode"),
    )



def normalize_meter_details(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        data = payload["nodes"][2]["data"]

        installed_meter = json.loads(data[3])["installed_meter"]

    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "Unexpected meter details response structure"
        ) from exc

    return {
        "meter_id": installed_meter.get("MeterId", data[1]),
        "serial_number": installed_meter.get("SerialNo"),
        "make": installed_meter.get("Make"),
        "phase_type": installed_meter.get("PhaseType"),
        "installation_status": installed_meter.get("InstallationStatus"),
        "installation_type": installed_meter.get("InstallationType"),
        "hierarchy": {
            "zone": data[7] if len(data) > 7 else None,
            "circle": data[8] if len(data) > 8 else None,
            "division": data[9] if len(data) > 9 else None,
            "subdivision": data[10] if len(data) > 10 else None,
            "substation": data[11] if len(data) > 11 else None,
            "feeder": data[12] if len(data) > 12 else None,
            "distribution_transformer": data[13] if len(data) > 13 else None,
        },
    }


def normalize_energy_reading(item: dict[str, Any]) -> EnergyReading:
    return EnergyReading(
        timestamp=item["timestamp"],
        kwh=float(item["kwh"]) if item.get("kwh") not in (None, "") else None,
        kvah=float(item["kvah"]) if item.get("kvah") not in (None, "") else None,
        volt=float(item["volt"]) if item.get("volt") not in (None, "") else None,
    )


def normalize_location(payload: dict[str, Any]) -> MeterLocation:
    data = payload.get("data", payload)

    return MeterLocation(
        latitude=float(data["latitude"]),
        longitude=float(data["longitude"]),
    )
