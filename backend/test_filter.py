import sys
import os
import struct
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import get_db_connection
from app.services.gemini import generate_embedding
from app.config import settings

def test_filter(query):
    print(f"Testing query: {query} (Threshold: {settings.SEARCH_THRESHOLD})")
    query_embedding = generate_embedding(query)
    embedding_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Try with Subquery
    cursor.execute('''
        SELECT * FROM (
            SELECT photo_id, vec_distance_cosine(description_embedding, ?) as distance
            FROM photo_embeddings
        ) WHERE distance < ?
    ''', (embedding_bytes, settings.SEARCH_THRESHOLD))
    
    rows = cursor.fetchall()
    print(f"Results found with Subquery: {len(rows)}")
    for row in rows:
        print(f"  Match: {row[0]} | Distance: {row[1]}")
    
    conn.close()

if __name__ == "__main__":
    test_filter("mutlu bir çocuk")
