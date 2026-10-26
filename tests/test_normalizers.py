import json

import pytest

from app.schemas.normalizers import (
    normalize_energy_reading,
    normalize_location,
    normalize_meter_details,
    normalize_meter_list_item,
)

def test_normalize_meter_list_item():
    result = normalize_meter_list_item(
        {
            "meterId": "J100000",
            "serialNo": "SE33962",
            "make": "HPL",
            "phaseType": "single",
            "installStatus": "Decommissioned",
            "dtCode": "DT-001",
        }
    )

    assert result.meter_id == "J100000"
    assert result.serial_number == "SE33962"
    assert result.make == "HPL"
    assert result.installation_status == "Decommissioned"
    assert result.dt_code == "DT-001"

def test_normalize_meter_details():
    data = [
        {"meterId": 1, "detail": 2, "hierarchy": 4},
        "J100004",
        {"classData": 3},
        json.dumps(
            {
                "installed_meter": {
                    "MeterId": "J100004",
                    "SerialNo": "SE65293",
                    "Make": "Genus",
                    "PhaseType": "single",
                    "InstallationStatus": "Faulty",
                    "InstallationType": "CT Operated",
                }
            }
        ),
        {
            "Meter ID": 1,
            "Installation Status": 5,
            "Installation Type": 6,
            "Zone": 7,
            "Circle": 8,
            "Division": 9,
            "Subdivision": 10,
            "Sub Station": 11,
            "Feeder": 12,
            "DT": 13,
        },
        "Faulty",
        "CT Operated",
        "Jaipur Zone 2 (Z-02)",
        "Circle 5 (C-05)",
        "Division 5 (D-05)",
        "Subdivision 5 (SD-05)",
        "Substation 5 (SS-05)",
        "Feeder 5 (F-005)",
        "Bani Park DT 5 (DT-005)",
    ]

    result = normalize_meter_details(
        {
            "type": "data",
            "nodes": [
                {"type": "skip"},
                {"type": "skip"},
                {"type": "data", "data": data},
            ],
        }
    )

    assert result["meter_id"] == "J100004"
    assert result["serial_number"] == "SE65293"
    assert result["installation_status"] == "Faulty"
    assert result["hierarchy"]["zone"] == "Jaipur Zone 2 (Z-02)"

def test_normalize_meter_details_rejects_invalid_structure():
    with pytest.raises(ValueError, match="Unexpected meter details"):
        normalize_meter_details({"type": "data", "nodes": []})

def test_normalize_energy_reading():
    result = normalize_energy_reading(
        {
            "timestamp": "23/06/2026 23:30",
            "kwh": "20403.4",
            "kvah": "22035.67",
            "volt": "239",
        }
    )

    assert result.kwh == pytest.approx(20403.4)
    assert result.kvah == pytest.approx(22035.67)
    assert result.volt == pytest.approx(239.0)

def test_normalize_location():
    result = normalize_location(
        {
            "data": {
                "latitude": "26.907425164505934",
                "longitude": "75.72503661059095",
            }
        }
    )

    assert result.latitude == pytest.approx(26.907425164505934)
    assert result.longitude == pytest.approx(75.72503661059095)
