from fastapi import FastAPI

app = FastAPI(title="YT", description="Video sharing service", version="0.1.0")


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "yt"}
