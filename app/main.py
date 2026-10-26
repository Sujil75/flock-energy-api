from fastapi import FastAPI
from app.api.meters import router as meter_router

app = FastAPI(
    title="Flock Energy API Adaptor",
    description="A REST API adapter for the legacy Flock Energy portal.",
    version="0.1.0",
)

app.include_router(meter_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
    }