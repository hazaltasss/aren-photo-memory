from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.database import get_db_connection
from app.config import settings
from app.schemas import PhotoResponse
from app.services.photo_service import process_and_save_photo
import uuid
import os
from datetime import datetime
import json
import shutil

router = APIRouter(prefix="/api/photos", tags=["Photos"])

@router.post("", response_model=PhotoResponse, status_code=201)
async def upload_photo(file: UploadFile = File(...)):
    photo_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{photo_id}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    try:
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return process_and_save_photo(file_path, file.filename)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/image/{filename}")
def get_image(filename: str):
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

@router.get("", response_model=list[PhotoResponse])
def list_photos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM photos ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        d = dict(row)
        d['is_smiling'] = bool(d['is_smiling'])
        d['is_crying'] = bool(d['is_crying'])
        d['has_other_people'] = bool(d['has_other_people'])
        d['is_funny'] = bool(d['is_funny'])
        d['objects'] = json.loads(d['objects']) if d['objects'] else []
        d['detected_people'] = json.loads(d['detected_people']) if d['detected_people'] else []
        results.append(PhotoResponse(**d))
    return results

@router.delete("/{photo_id}", status_code=204)
def delete_photo(photo_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT file_url FROM photos WHERE id = ?", (photo_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Photo not found")
        
    file_url = row['file_url']
    filename = file_url.split('/')[-1]
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    cursor.execute("DELETE FROM photo_embeddings WHERE photo_id = ?", (photo_id,))
    cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
    conn.commit()
    conn.close()
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    return None
