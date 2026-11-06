from google import genai
from google.genai import types
from app.config import settings
from app.schemas import PhotoAnalysisResult
import json
import time

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_gemini_model():
    """WhatsApp mesajlarını analiz etmek için Gemini model nesnesini döner."""
    # Yeni SDK'da generate_content doğrudan client.models üzerinden yapılıyor
    return client.models

def analyze_photo(image_path: str) -> PhotoAnalysisResult:
    uploaded_file = client.files.upload(file=image_path)
    
    prompt = """
    Analyze this photo of a 2-year-old toddler named Aren. 
    Extract the following structured information and provide a detailed description.
    
    IMPORTANT: The fields 'emotion', 'is_smiling', and 'is_crying' MUST refer ONLY to Aren. 
    Ignore the expressions of other people in the background or next to him. 
    For example, if Aren is neutral but his mother is smiling, 'is_smiling' MUST be false and 'emotion' MUST be 'nötr'.
    
    IMPORTANT: ALL text fields and categorical values MUST be in TURKISH.
    
    Return strictly a JSON object matching this schema:
    {
      "emotion": "mutlu/üzgün/şaşkın/nötr/kızgın/heyecanlı/uykulu",
      "is_smiling": boolean,
      "is_crying": boolean,
      "activity": "aktiviteyi tanımlayan kısa metin",
      "location_type": "iç mekan/dış mekan",
      "location_detail": "kısa metin (örn: park, ev, plaj)",
      "people_count": integer,
      "has_other_people": boolean,
      "detected_people": ["aren", "anne", "baba", "diğer"],
      "clothing_description": "kısa kıyafet tanımı",
      "hair_length": "kısa/orta/uzun",
      "is_funny": boolean,
      "funniness_score": integer 1-10,
      "cuteness_score": integer 1-10,
      "objects": ["nesne", "listesi"],
      "season_guess": "ilkbahar/yaz/sonbahar/kış",
      "description": "Fotoğrafın detaylı doğal dildeki Türkçe açıklaması."
    }
    
    NOT: 'detected_people' alanı her zaman Aren'ı içermelidir (eğer oradaysa). Annesi için 'anne', babası için 'baba' etiketlerini kullan.
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            if "503" in str(e) or "429" in str(e):
                print(f"⚠️ Gemini meşgul (Deneme {attempt+1}/{max_retries}). 2 saniye bekleniyor...")
                time.sleep(2)
            else:
                raise e
    
    
    data = json.loads(response.text)
    return PhotoAnalysisResult(**data)

def generate_embedding(text: str) -> list[float]:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            if "503" in str(e) or "429" in str(e):
                time.sleep(2)
            else:
                raise e
