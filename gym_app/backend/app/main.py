from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.db import engine
from app.migrate import run_migrations
from app.routers import admin, attendance, auth, qr, schools

_TEACHER_UI = Path(__file__).resolve().parent.parent / "static" / "teacher" / "index.html"
_TEACHER_SETUP = Path(__file__).resolve().parent.parent / "static" / "teacher" / "setup.html"
_TEACHER_KIOSK = Path(__file__).resolve().parent.parent / "static" / "teacher" / "kiosk.html"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    run_migrations(engine)
    yield


app = FastAPI(title="Gym Attendance API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(schools.router)
app.include_router(qr.router)
app.include_router(attendance.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/teacher")
def teacher_desk():
    """Staff browser UI: attendance table + rotating door QR (admin login)."""
    return FileResponse(_TEACHER_UI)


@app.get("/teacher/setup")
def teacher_new_school():
    """Create a new school + master admin (strong password)."""
    return FileResponse(_TEACHER_SETUP)


@app.get("/teacher/kiosk")
def teacher_kiosk_qr_only():
    """Minimal full-screen door QR; admin login required (same session as /teacher)."""
    return FileResponse(_TEACHER_KIOSK)
