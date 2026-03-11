from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from api.preview import generate_preview

app = FastAPI(title="Response Stats Preview API")

# Replace with your actual GitHub Pages domain later
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3000/",
    "https://a-darcher.github.io",
    "https://a-darcher.github.io/response_generator",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://a-darcher.github.io",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PreviewRequest(BaseModel):
    # Replace these with your real parameters
    sample_size: int = Field(default=100, ge=10, le=5000)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    scale: float = Field(default=1.0, ge=0.1, le=5.0)
    seed: int = Field(default=42, ge=0, le=999999)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/preview")
def preview(req: PreviewRequest):
    try:
        result = generate_preview(
            sample_size=req.sample_size,
            threshold=req.threshold,
            scale=req.scale,
            seed=req.seed,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))