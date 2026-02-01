from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime
import uuid

from app.core.databace import get_db
from app.models.image import SatelliteImage
from app.schemas.image import ImageResponse

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    date_captured: datetime = None,
    db: Session = Depends(get_db)
):
    """Загрузка спутникового снимка"""
    try:
        # Генерируем уникальное имя
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        filepath = f"data/raw/{unique_filename}"
        
        # Создаем директорию
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Сохраняем файл
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Создаем запись в БД
        db_image = SatelliteImage(
            filename=unique_filename,
            filepath=filepath,
            date_captured=date_captured or datetime.now(),
            resolution=1.0,
            width=1920,
            height=1080
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return db_image
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

@router.get("/", response_model=list[ImageResponse])
def get_images(db: Session = Depends(get_db)):
    """Получение списка всех изображений"""
    return db.query(SatelliteImage).order_by(SatelliteImage.created_at.desc()).all()