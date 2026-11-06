import uuid
import os
from datetime import datetime
import json
import struct
from fastapi import HTTPException
from app.services.gemini import analyze_photo, generate_embedding
from app.database import get_db_connection
from app.config import settings
from app.schemas import PhotoResponse

def process_and_save_photo(file_path: str, original_filename: str = None) -> PhotoResponse:
    """
    Analyzes a photo with Gemini, generates embeddings, and saves it to the database.
    Assumes the file is already saved to file_path.
    original_filename is used to extract extension if needed, but file_path's name is used for the DB URL.
    """
    filename = os.path.basename(file_path)
    photo_id = os.path.splitext(filename)[0]
    
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
                has_other_people, detected_people, clothing_description, hair_length,
                is_funny, funniness_score, cuteness_score, objects,
                season_guess, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            photo_id, file_url, now, analysis.emotion, 1 if analysis.is_smiling else 0,
            1 if analysis.is_crying else 0, analysis.activity, analysis.location_type,
            analysis.location_detail, analysis.people_count, 
            1 if analysis.has_other_people else 0, json.dumps(analysis.detected_people),
            analysis.clothing_description,
            analysis.hair_length, 1 if analysis.is_funny else 0, 
            analysis.funniness_score, analysis.cuteness_score,
            json.dumps(analysis.objects), analysis.season_guess, analysis.description
        ))
        
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
        # If processing fails, we don't necessarily delete the file here, 
        # but the caller might. Let's let the caller handle file cleanup on error.
        raise e
