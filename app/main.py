from fastapi import FastAPI

app = FastAPI(
    title="Flock Energy API Adaptor",
    description="A REST API adapter for the legacy Flock Energy portal.",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
    }