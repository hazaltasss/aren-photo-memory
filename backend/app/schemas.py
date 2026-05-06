from pydantic import BaseModel
from typing import List, Optional

class PhotoAnalysisResult(BaseModel):
    emotion: str
    is_smiling: bool
    is_crying: bool
    activity: str
    location_type: str
    location_detail: str
    people_count: int
    has_other_people: bool
    clothing_description: str
    hair_length: str
    is_funny: bool
    funniness_score: int
    cuteness_score: int
    objects: List[str]
    season_guess: str
    description: str

class PhotoResponse(PhotoAnalysisResult):
    id: str
    file_url: str
    uploaded_at: str
    photo_date: Optional[str] = None
    notes: Optional[str] = None
