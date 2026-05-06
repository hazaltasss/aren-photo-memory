from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gemini import generate_embedding
from app.database import get_db_connection
from app.schemas import PhotoResponse
from app.config import settings
import json

router = APIRouter(prefix="/api/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    limit: int = 20

@router.post("", response_model=list[PhotoResponse])
def search_photos(req: SearchRequest):
    try:
        query_embedding = generate_embedding(req.query)
        import struct
        embedding_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Semantic search using sqlite-vec with threshold
        cursor.execute('''
            WITH matches AS (
                SELECT photo_id, vec_distance_cosine(description_embedding, ?) as distance
                FROM photo_embeddings
                WHERE distance < ?
                ORDER BY distance ASC
                LIMIT ?
            )
            SELECT p.*, m.distance
            FROM matches m
            JOIN photos p ON m.photo_id = p.id
        ''', (embedding_bytes, settings.SEARCH_THRESHOLD, req.limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            d = dict(row)
            d.pop('distance', None) # Remove distance from response
            d['is_smiling'] = bool(d['is_smiling'])
            d['is_crying'] = bool(d['is_crying'])
            d['has_other_people'] = bool(d['has_other_people'])
            d['is_funny'] = bool(d['is_funny'])
            d['objects'] = json.loads(d['objects']) if d['objects'] else []
            results.append(PhotoResponse(**d))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
