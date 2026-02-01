from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.core.databace import Base

class SatelliteImage(Base):
    __tablename__ = "satellite_images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    date_captured = Column(DateTime, nullable=False)
    coordinates = Column(Text, nullable=True)
    resolution = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SatelliteImage(id={self.id}, filename='{self.filename}')>"