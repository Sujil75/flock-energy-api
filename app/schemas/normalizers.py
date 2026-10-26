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

        # Format 1: installed_meter is serialized as a JSON string.
        if isinstance(data[3], str):
            installed_meter = json.loads(data[3])["installed_meter"]

            meter_id = installed_meter.get("MeterId", data[1])
            serial_number = installed_meter.get("SerialNo")
            make = installed_meter.get("Make")
            phase_type = installed_meter.get("PhaseType")
            installation_status = installed_meter.get("InstallationStatus")
            installation_type = installed_meter.get("InstallationType")

            hierarchy = {
                "zone": data[7] if len(data) > 7 else None,
                "circle": data[8] if len(data) > 8 else None,
                "division": data[9] if len(data) > 9 else None,
                "subdivision": data[10] if len(data) > 10 else None,
                "substation": data[11] if len(data) > 11 else None,
                "feeder": data[12] if len(data) > 12 else None,
                "distribution_transformer": data[13] if len(data) > 13 else None,
            }

        # Format 2: fields are stored at indexed positions.
        else:
            meter_id = data[1]
            serial_number = None
            make = None
            phase_type = None
            installation_status = None
            installation_type = None

            for item in data:
                if not isinstance(item, dict):
                    continue

                name = item.get("parameterName")
                value = item.get("parameterValue")

                if name is None or value is None:
                    continue

                if name >= len(data) or value >= len(data):
                    continue

                field_name = data[name]
                field_value = data[value]

                if field_name == "Serial No":
                    serial_number = field_value
                elif field_name == "Make":
                    make = field_value
                elif field_name == "Phase Type":
                    phase_type = field_value
                elif field_name == "Installation Status":
                    installation_status = field_value
                elif field_name == "Installation Type":
                    installation_type = field_value

            hierarchy_data = next(
                (
                    item
                    for item in data
                    if isinstance(item, dict) and "Zone" in item
                ),
                {},
            )

            hierarchy = {
                "zone": data[hierarchy_data["Zone"]]
                if hierarchy_data.get("Zone", -1) < len(data)
                else None,
                "circle": data[hierarchy_data["Circle"]]
                if hierarchy_data.get("Circle", -1) < len(data)
                else None,
                "division": data[hierarchy_data["Division"]]
                if hierarchy_data.get("Division", -1) < len(data)
                else None,
                "subdivision": data[hierarchy_data["Subdivision"]]
                if hierarchy_data.get("Subdivision", -1) < len(data)
                else None,
                "substation": data[hierarchy_data["Sub Station"]]
                if hierarchy_data.get("Sub Station", -1) < len(data)
                else None,
                "feeder": data[hierarchy_data["Feeder"]]
                if hierarchy_data.get("Feeder", -1) < len(data)
                else None,
                "distribution_transformer": data[hierarchy_data["DT"]]
                if hierarchy_data.get("DT", -1) < len(data)
                else None,
            }

    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(
            "Unexpected meter details response structure"
        ) from exc

    return {
        "meter_id": meter_id,
        "serial_number": serial_number,
        "make": make,
        "phase_type": phase_type,
        "installation_status": installation_status,
        "installation_type": installation_type,
        "hierarchy": hierarchy,
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
