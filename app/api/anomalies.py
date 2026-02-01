from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import random

from app.core.databace import get_db
from app.models.anomaly import Anomaly
from app.schemas.anomaly import AnomalyResponse

router = APIRouter(prefix="/anomalies", tags=["anomalies"])

@router.get("/", response_model=List[AnomalyResponse])
def get_anomalies(
    anomaly_type: Optional[str] = Query(None),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Получение аномалий (реальные + демо данные)"""
    try:
        # Пробуем получить из БД
        query = db.query(Anomaly)
        if anomaly_type:
            query = query.filter(Anomaly.anomaly_type == anomaly_type)
        query = query.filter(Anomaly.confidence >= min_confidence)
        
        db_anomalies = query.order_by(Anomaly.detected_at.desc()).all()
        
        if db_anomalies:
            return db_anomalies
        else:
            # Если в БД нет данных, возвращаем демо
            return get_demo_anomalies(anomaly_type, min_confidence)
            
    except Exception as e:
        # При любой ошибке возвращаем демо данные
        return get_demo_anomalies(anomaly_type, min_confidence)

def get_demo_anomalies(anomaly_type: Optional[str] = None, min_confidence: float = 0.5):
    """Генерация демо аномалий"""
    anomaly_types = ['fire', 'deforestation', 'dump', 'construction', 'flood']
    
    if anomaly_type and anomaly_type in anomaly_types:
        types = [anomaly_type]
    else:
        types = anomaly_types
    
    anomalies = []
    for i in range(10):
        a_type = random.choice(types)
        confidence = round(random.uniform(min_confidence, 0.95), 2)
        
        anomalies.append({
            "id": i + 1,
            "anomaly_type": a_type,
            "confidence": confidence,
            "latitude": 55.7558 + random.uniform(-0.5, 0.5),
            "longitude": 37.6173 + random.uniform(-0.5, 0.5),
            "description": get_anomaly_description(a_type, confidence),
            "detected_at": datetime.now() - timedelta(days=random.randint(0, 30)),
            "image_id": random.randint(1, 5)
        })
    
    return anomalies

def get_anomaly_description(anomaly_type: str, confidence: float) -> str:
    descriptions = {
        'fire': [
            'Лесной пожар, требуется тушение',
            'Торфяной пожар, высокая опасность',
            'Пожар на сельхозугодьях'
        ],
        'deforestation': [
            'Незаконная вырубка леса',
            'Расчистка территории под застройку',
            'Вырубка леса для сельского хозяйства'
        ],
        'dump': [
            'Несанкционированная свалка',
            'Скопление строительного мусора',
            'Загрязнение территории отходами'
        ],
        'construction': [
            'Незаконное строительство',
            'Строительные работы в охраняемой зоне',
            'Изменение ландшафта под застройку'
        ],
        'flood': [
            'Затопление территории',
            'Паводок, подтопление домов',
            'Подтопление сельхозугодий'
        ]
    }
    
    desc_list = descriptions.get(anomaly_type, ['Обнаружена аномалия'])
    desc = random.choice(desc_list)
    
    if confidence > 0.8:
        severity = 'высокая опасность'
    elif confidence > 0.6:
        severity = 'средняя опасность'
    else:
        severity = 'низкая опасность'
    
    return f"{desc} ({severity})"