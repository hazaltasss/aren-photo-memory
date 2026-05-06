from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gemini import generate_embedding
from app.database import get_db_connection
from app.schemas import PhotoResponse
from app.config import settings
import json
import struct

router = APIRouter(prefix="/api/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str

@router.post("", response_model=list[PhotoResponse])
def search_photos(req: SearchRequest):
    try:
        query_embedding = generate_embedding(req.query)
        embedding_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch top-N results ordered by distance, no WHERE filter
        cursor.execute('''
            SELECT p.*, m.distance
            FROM (
                SELECT photo_id, vec_distance_cosine(description_embedding, ?) as distance
                FROM photo_embeddings
                ORDER BY distance ASC
                LIMIT ?
            ) m
            JOIN photos p ON m.photo_id = p.id
        ''', (embedding_bytes, settings.SEARCH_LIMIT))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        # Apply gap filter in Python: drop anything beyond best_distance + SEARCH_GAP
        best_distance = rows[0]['distance']
        cutoff = best_distance + settings.SEARCH_GAP

        results = []
        for row in rows:
            d = dict(row)
            distance = d.pop('distance')

            if distance > cutoff:
                break  # Results are ordered, so we can stop early

            d['is_smiling'] = bool(d['is_smiling'])
            d['is_crying'] = bool(d['is_crying'])
            d['has_other_people'] = bool(d['has_other_people'])
            d['is_funny'] = bool(d['is_funny'])
            d['objects'] = json.loads(d['objects']) if d['objects'] else []
            d['relevance'] = max(0, int((1 - distance) * 100))
            results.append(PhotoResponse(**d))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
