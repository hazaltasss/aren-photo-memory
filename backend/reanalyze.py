import os
import json
import sqlite3
from app.database import get_db_connection
from app.services.gemini import analyze_photo
from app.config import settings

def reanalyze_all_photos():
    print("🛡️ Aren Photo Memory - Toplu Analiz Başlatılıyor...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tüm fotoğrafları getir
    cursor.execute("SELECT id, file_url FROM photos")
    photos = cursor.fetchall()
    
    print(f"📦 Toplam {len(photos)} fotoğraf taranacak.")
    
    for photo in photos:
        photo_id = photo['id']
        file_url = photo['file_url']
        
        # Dosya yolunu oluştur (URL'den dosya ismini al)
        filename = file_url.split('/')[-1]
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠️ Dosya bulunamadı: {file_path}")
            continue
            
        print(f"🔍 Analiz ediliyor ({photo_id}): {filename}...")
        
        try:
            # Gemini ile tekrar analiz et (Yeni şema ile)
            analysis = analyze_photo(file_path)
            
            # Veritabanını güncelle
            cursor.execute('''
                UPDATE photos 
                SET detected_people = ?, 
                    emotion = ?, 
                    is_smiling = ?,
                    description = ?
                WHERE id = ?
            ''', (
                json.dumps(analysis.detected_people),
                analysis.emotion,
                1 if analysis.is_smiling else 0,
                analysis.description,
                photo_id
            ))
            conn.commit()
            print(f"✅ Başarıyla güncellendi: {analysis.detected_people}")
            
        except Exception as e:
            print(f"🚨 Hata oluştu ({photo_id}): {e}")
            
    conn.close()
    print("✨ Tüm hafıza başarıyla güncellendi!")

if __name__ == "__main__":
    reanalyze_all_photos()
