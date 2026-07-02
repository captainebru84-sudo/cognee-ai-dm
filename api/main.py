"""FastAPI shim exposing narrate() to the Next.js UI.

Run from repo root:
    uvicorn api.main:app --reload --port 8000
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dm import narrate


class NarrateIn(BaseModel):
    player_action: str


class NarrateOut(BaseModel):
    narration: str


app = FastAPI(title="cognee-ai-dm")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.post("/narrate", response_model=NarrateOut)
async def narrate_endpoint(payload: NarrateIn) -> NarrateOut:
    narration = await narrate(payload.player_action)
    return NarrateOut(narration=narration)
