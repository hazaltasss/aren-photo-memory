from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services.gemini import analyze_photo, generate_embedding
from app.database import get_db_connection
from app.config import settings
from app.schemas import PhotoResponse
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
    
    # Save file locally
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Analyze with Gemini
        analysis = analyze_photo(file_path)
        
        # Generate embedding for the description
        embedding = generate_embedding(analysis.description)
        
        # Save to SQLite
        file_url = f"/api/photos/image/{filename}"
        now = datetime.utcnow().isoformat()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO photos (
                id, file_url, uploaded_at, emotion, is_smiling, is_crying,
                activity, location_type, location_detail, people_count,
                has_other_people, clothing_description, hair_length,
                is_funny, funniness_score, cuteness_score, objects,
                season_guess, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            photo_id, file_url, now, analysis.emotion, 1 if analysis.is_smiling else 0,
            1 if analysis.is_crying else 0, analysis.activity, analysis.location_type,
            analysis.location_detail, analysis.people_count, 
            1 if analysis.has_other_people else 0, analysis.clothing_description,
            analysis.hair_length, 1 if analysis.is_funny else 0, 
            analysis.funniness_score, analysis.cuteness_score,
            json.dumps(analysis.objects), analysis.season_guess, analysis.description
        ))
        
        import struct
        embedding_bytes = struct.pack(f'{len(embedding)}f', *embedding)
        cursor.execute('''
            INSERT INTO photo_embeddings (photo_id, description_embedding)
            VALUES (?, ?)
        ''', (photo_id, embedding_bytes))
        
        conn.commit()
        conn.close()
        
        return PhotoResponse(
            id=photo_id,
            file_url=file_url,
            uploaded_at=now,
            **analysis.model_dump()
        )
    except Exception as e:
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
        results.append(PhotoResponse(**d))
    return results
