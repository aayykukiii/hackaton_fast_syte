from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ImageBase(BaseModel):
    filename: str
    date_captured: datetime

class ImageCreate(ImageBase):
    filepath: str

class ImageResponse(ImageBase):
    id: int
    filepath: str
    created_at: datetime
    
    class Config:
        from_attributes = True