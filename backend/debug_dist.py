import sys
import os
import struct
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import get_db_connection
from app.services.gemini import generate_embedding

def check_distance(query):
    query_embedding = generate_embedding(query)
    embedding_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, vec_distance_cosine(e.description_embedding, ?) as distance
        FROM photo_embeddings e
        JOIN photos p ON e.photo_id = p.id
    ''', (embedding_bytes,))
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"Query: {query} | Photo ID: {row[0]} | Distance: {row[1]}")
    conn.close()

if __name__ == "__main__":
    check_distance("mutlu bir çocuk")
    check_distance("uzay gemisi")
