from google import genai
from google.genai import types
from app.config import settings
from app.schemas import PhotoAnalysisResult
import json

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def analyze_photo(image_path: str) -> PhotoAnalysisResult:
    # Upload file to Gemini API for processing
    uploaded_file = client.files.upload(file=image_path)
    
    prompt = """
    Analyze this photo of a 2-year-old toddler named Aren. 
    Extract the following structured information and provide a detailed description.
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
      "clothing_description": "kısa kıyafet tanımı",
      "hair_length": "kısa/orta/uzun",
      "is_funny": boolean,
      "funniness_score": integer 1-10,
      "cuteness_score": integer 1-10,
      "objects": ["nesne", "listesi"],
      "season_guess": "ilkbahar/yaz/sonbahar/kış",
      "description": "Fotoğrafın detaylı doğal dildeki Türkçe açıklaması."
    }
    """
    
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[uploaded_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    data = json.loads(response.text)
    return PhotoAnalysisResult(**data)

def generate_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=text
    )
    return response.embeddings[0].values
