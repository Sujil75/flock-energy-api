from pydantic import BaseModel, ConfigDict, Field

class MeterResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    meter_id: str = Field(description="Unique meter identifier")
    serial_number: str | None = None
    make: str | None = None
    phase_type: str | None = None
    installation_status: str | None = None
    installation_type: str | None = None
    dt_code: str | None = None


class MeterListResponse(BaseModel):
    data: list[MeterResponse] = Field(
        description="List of meters returned by the legacy portal"
    )


class EnergyReading(BaseModel):
    timestamp: str
    kwh: float | None = None
    kvah: float | None = None
    volt: float | None = None


class MeterLocation(BaseModel):
    latitude: float
    longitude: float
