from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas import PhotoResponse
from app.services.search_service import perform_search
from app.config import settings
from typing import List, Optional
import json

router = APIRouter(prefix="/api/search", tags=["Search"])

class SearchFilters(BaseModel):
    emotions: Optional[List[str]] = None
    location_types: Optional[List[str]] = None
    objects: Optional[List[str]] = None
    detected_people: Optional[List[str]] = None
    hair_length: Optional[str] = None

class SearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[SearchFilters] = None

@router.post("", response_model=list[PhotoResponse])
def search_photos(req: SearchRequest):
    try:
        filters_dict = req.filters.dict(exclude_none=True) if req.filters else {}
        rows = perform_search(query=req.query, filters=filters_dict, limit=settings.SEARCH_LIMIT)
        
        results = []
        best_distance = rows[0]['distance'] if rows and rows[0]['distance'] is not None else None
        
        for row in rows:
            d = dict(row)
            distance = d.pop('distance')
            
            if distance is not None and best_distance is not None:
                if distance > best_distance + settings.SEARCH_GAP:
                    break
                d['relevance'] = max(0, int((1 - distance) * 100))
            else:
                d['relevance'] = None

            d['is_smiling'] = bool(d['is_smiling'])
            d['is_crying'] = bool(d['is_crying'])
            d['has_other_people'] = bool(d['has_other_people'])
            d['is_funny'] = bool(d['is_funny'])
            d['objects'] = json.loads(d['objects']) if d['objects'] else []
            d['detected_people'] = json.loads(d['detected_people']) if d.get('detected_people') else []
            results.append(PhotoResponse(**d))

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
