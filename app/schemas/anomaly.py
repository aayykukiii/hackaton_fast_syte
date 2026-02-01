from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnomalyBase(BaseModel):
    anomaly_type: str
    confidence: float
    latitude: float
    longitude: float

class AnomalyCreate(AnomalyBase):
    image_id: int

class AnomalyResponse(AnomalyBase):
    id: int
    image_id: int
    description: Optional[str] = None
    detected_at: datetime
    
    class Config:
        from_attributes = True