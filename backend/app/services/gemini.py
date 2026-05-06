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
    Return strictly a JSON object matching this schema:
    {
      "emotion": "happy/sad/surprised/neutral/angry/excited/sleepy",
      "is_smiling": boolean,
      "is_crying": boolean,
      "activity": "short string describing activity",
      "location_type": "indoor/outdoor",
      "location_detail": "short string (e.g., park, house, beach)",
      "people_count": integer,
      "has_other_people": boolean,
      "clothing_description": "short string",
      "hair_length": "short/medium/long",
      "is_funny": boolean,
      "funniness_score": integer 1-10,
      "cuteness_score": integer 1-10,
      "objects": ["array", "of", "strings"],
      "season_guess": "spring/summer/fall/winter",
      "description": "Detailed natural language description of the photo."
    }
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[uploaded_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    data = json.loads(response.text)
    return PhotoAnalysisResult(**data)

def generate_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model='text-embedding-004',
        contents=text
    )
    return response.embeddings[0].values
