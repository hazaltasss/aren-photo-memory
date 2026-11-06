import json
import struct
from app.database import get_db_connection
from app.services.gemini import generate_embedding
from app.config import settings

def perform_search(query: str = None, filters: dict = None, limit: int = 20):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        where_clauses = []
        params = []

        if filters:
            if filters.get("emotions"):
                placeholders = ",".join(["?" for _ in filters["emotions"]])
                where_clauses.append(f"p.emotion IN ({placeholders})")
                params.extend([e.lower() for e in filters["emotions"]])
            
            if filters.get("location_types"):
                placeholders = ",".join(["?" for _ in filters["location_types"]])
                where_clauses.append(f"p.location_type IN ({placeholders})")
                params.extend([l.lower() for l in filters["location_types"]])
            
            if filters.get("objects"):
                for obj in filters["objects"]:
                    where_clauses.append("p.objects LIKE ?")
                    params.append(f"%{obj.lower()}%")
            
            if filters.get("detected_people"):
                for person in filters["detected_people"]:
                    where_clauses.append("p.detected_people LIKE ?")
                    params.append(f"%{person.lower()}%")

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        if query:
            query_embedding = generate_embedding(query)
            embedding_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)
            
            sql = f'''
                SELECT p.*, m.distance
                FROM (
                    SELECT photo_id, vec_distance_cosine(description_embedding, ?) as distance
                    FROM photo_embeddings
                ) m
                JOIN photos p ON m.photo_id = p.id
                WHERE ({where_sql})
                ORDER BY m.distance ASC
                LIMIT ?
            '''
            final_params = [embedding_bytes] + params + [limit]
            cursor.execute(sql, final_params)
        else:
            sql = f'''
                SELECT p.*, NULL as distance
                FROM photos p
                WHERE {where_sql}
                ORDER BY p.uploaded_at DESC
                LIMIT ?
            '''
            final_params = params + [limit]
            cursor.execute(sql, final_params)

        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Search error: {e}")
        return []
