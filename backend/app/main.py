from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
import os
from app.config import settings
from app.routers import photos, search, filters, whatsapp

app = FastAPI(title="Aren Photo Memory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_db()

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Serve uploads directory
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(photos.router)
app.include_router(search.router)
app.include_router(filters.router)
app.include_router(whatsapp.router)
