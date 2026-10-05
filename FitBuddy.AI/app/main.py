from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .routes import router


BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(
    title="FitBuddy AI Fitness Plan Generator",
    description=(
        "AI-powered personalized fitness planning "
        "with Gemini."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.cors_origin_list,

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            BASE_DIR / "static"
        )
    ),
    name="static",
)


app.include_router(router)


@app.on_event("startup")
def startup() -> None:

    init_db()