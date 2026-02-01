from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter(prefix="/demo", tags=["demo"])

@router.get("/test-analysis")
async def test_analysis():
    """Тестовый анализ - ВСЕГДА работает"""
    return {
        "status": "completed",
        "anomalies_found": 5,
        "processing_time": f"{random.uniform(1.5, 3.2):.1f}s",
        "message": "Тестовый анализ выполнен успешно! Обнаружено 5 аномалий.",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "fire": 2,
            "deforestation": 1,
            "dump": 1,
            "construction": 1
        }
    }

@router.get("/analyze/{image_id}")
async def analyze_image(image_id: int):
    """Анализ конкретного изображения (демо)"""
    return {
        "image_id": image_id,
        "status": "analyzed",
        "anomalies": [
            {"type": "fire", "confidence": 0.87, "area": "северная часть"},
            {"type": "deforestation", "confidence": 0.65, "area": "юго-запад"}
        ],
        "message": f"Изображение #{image_id} проанализировано",
        "recommendation": "Требуется проверка на месте"
    }

@router.get("/compare")
async def compare_images(image1_id: int = 1, image2_id: int = 2):
    """Сравнение двух изображений (демо)"""
    return {
        "comparison": {
            "image1": f"Снимок #{image1_id} (2023 г.)",
            "image2": f"Снимок #{image2_id} (2024 г.)",
            "changes_found": 3,
            "change_areas": [
                {"type": "deforestation", "area_ha": 2.5, "confidence": 0.78},
                {"type": "construction", "area_ha": 0.8, "confidence": 0.62},
                {"type": "fire", "area_ha": 1.2, "confidence": 0.85}
            ],
            "total_change_area": "4.5 га",
            "change_percentage": "12%"
        },
        "message": "Обнаружены значительные изменения территории",
        "severity": "high"
    }

@router.get("/generate-report")
async def generate_report():
    """Генерация отчета (демо)"""
    return {
        "report_id": f"RPT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        "status": "generated",
        "download_url": "/api/demo/download-report",
        "content": {
            "summary": "Обнаружено 5 экологических нарушений",
            "anomalies": [
                "Лесной пожар - высокая опасность",
                "Незаконная вырубка - средняя опасность",
                "Несанкционированная свалка - низкая опасность"
            ],
            "recommendations": [
                "Срочное тушение пожара",
                "Проверка лесного участка",
                "Уборка свалки"
            ]
        }
    }

@router.get("/system-status")
async def system_status():
    """Статус системы"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "uptime": f"{random.randint(100, 1000)} часов",
        "components": {
            "api": "online",
            "database": "online",
            "analysis": "online",
            "storage": "online"
        },
        "last_updated": datetime.now().isoformat()
    }