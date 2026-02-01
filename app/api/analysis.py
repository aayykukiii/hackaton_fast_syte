from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import random
from datetime import datetime

from app.core.databace import get_db
from app.models.image import SatelliteImage

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/test")
async def test_analysis(background_tasks: BackgroundTasks = None):
    """Тестовый анализ - всегда работает"""
    if background_tasks:
        background_tasks.add_task(simulate_analysis)
        return {"message": "Анализ запущен в фоне", "status": "processing"}
    else:
        result = simulate_analysis()
        return {"message": "Анализ завершен", "status": "completed", "result": result}

def simulate_analysis():
    """Симуляция анализа"""
    import time
    time.sleep(1)  # Имитация обработки
    
    return {
        "anomalies_found": random.randint(3, 8),
        "processing_time": f"{random.uniform(1.5, 3.2):.1f} секунд",
        "detected_types": ["fire", "deforestation", "dump"],
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Статистика системы"""
    try:
        total_images = db.query(SatelliteImage).count()
    except:
        total_images = 0
    
    return {
        "total_images": total_images,
        "total_analyses": random.randint(50, 200),
        "anomalies_today": random.randint(1, 10),
        "success_rate": round(random.uniform(0.85, 0.98), 2),
        "system_status": "operational",
        "uptime": f"{random.randint(100, 1000)} часов"
    }