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

class MeterHierarchy(BaseModel):
    zone: str | None = None
    circle: str | None = None
    division: str | None = None
    subdivision: str | None = None
    substation: str | None = None
    feeder: str | None = None
    distribution_transformer: str | None = None

class MeterDetailsResponse(BaseModel):
    meter_id: str
    serial_number: str | None = None
    make: str | None = None
    phase_type: str | None = None
    installation_status: str | None = None
    installation_type: str | None = None
    hierarchy: MeterHierarchy
