from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from typing import List, Dict

router = APIRouter(prefix="/api/filters", tags=["Filters"])

@router.get("/options")
def get_filter_options():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Benzersiz Duyguları al
        cursor.execute("SELECT DISTINCT emotion FROM photos")
        emotions = [row[0] for row in cursor.fetchall() if row[0]]
        
        # Benzersiz Mekan detaylarını al
        cursor.execute("SELECT DISTINCT location_detail FROM photos")
        locations = [row[0] for row in cursor.fetchall() if row[0]]
        
        # En popüler nesneleri al (basit bir yaklaşım)
        # Not: JSON formatındaki nesneleri saymak için tabloyu tarıyoruz
        cursor.execute("SELECT objects FROM photos")
        all_objects = {}
        for row in cursor.fetchall():
            import json
            objs = json.loads(row[0]) if row[0] else []
            for obj in objs:
                all_objects[obj] = all_objects.get(obj, 0) + 1
        
        # En çok geçen ilk 10 nesne
        sorted_objects = sorted(all_objects.items(), key=lambda x: x[1], reverse=True)
        top_objects = [item[0] for item in sorted_objects[:10]]
        
        conn.close()
        
        return {
            "emotions": emotions,
            "locations": locations,
            "top_objects": top_objects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
