from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# Создаем директории
os.makedirs("app/static", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

app = FastAPI(
    title="Geo Anomaly Detector",
    description="Система автоматического мониторинга земной поверхности",
    version="1.0.0",
    debug=True
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

# Импорт API
try:
    from app.api import images, anomalies, analysis
    app.include_router(images.router, prefix="/api")
    app.include_router(anomalies.router, prefix="/api")
    app.include_router(analysis.router, prefix="/api")
    print("✅ API роутеры загружены")
except Exception as e:
    print(f"⚠️ Ошибка загрузки API: {e}")

# Глобальный поиск API (встроен в main.py для простоты)
from fastapi import Query
from datetime import datetime
import random

@app.get("/api/global/countries")
async def get_countries():
    countries = ["Россия", "Германия", "Испания", "США", "Китай", "Бразилия", "Австралия", "Франция", "Италия", "Канада"]
    return {"countries": countries, "count": len(countries)}

@app.get("/api/global/search/{country}")
async def search_by_country(country: str, year: int = Query(None)):
    # Демо данные для каждой страны
    country_data = {
        "Россия": {"capital": "Москва", "coords": [55.7558, 37.6173], "fires": 42, "deforestation": 28},
        "Германия": {"capital": "Берлин", "coords": [52.5200, 13.4050], "fires": 18, "deforestation": 12},
        "Испания": {"capital": "Мадрид", "coords": [40.4168, -3.7038], "fires": 35, "deforestation": 15},
        "США": {"capital": "Вашингтон", "coords": [38.9072, -77.0369], "fires": 87, "deforestation": 42},
        "Китай": {"capital": "Пекин", "coords": [39.9042, 116.4074], "fires": 56, "deforestation": 38}
    }
    
    if country in country_data:
        data = country_data[country]
        return {
            "country": country,
            "found": True,
            "capital": data["capital"],
            "coordinates": data["coords"],
            "statistics": {
                "fires": data["fires"],
                "deforestation": data["deforestation"],
                "total": data["fires"] + data["deforestation"]
            },
            "anomalies": [
                {
                    "id": 1,
                    "anomaly_type": "fire",
                    "latitude": data["coords"][0] + random.uniform(-0.5, 0.5),
                    "longitude": data["coords"][1] + random.uniform(-0.5, 0.5),
                    "confidence": round(random.uniform(0.6, 0.95), 2),
                    "description": f"Лесной пожар в {country}",
                    "date": "2024-01-15"
                },
                {
                    "id": 2,
                    "anomaly_type": "deforestation",
                    "latitude": data["coords"][0] + random.uniform(-0.5, 0.5),
                    "longitude": data["coords"][1] + random.uniform(-0.5, 0.5),
                    "confidence": round(random.uniform(0.5, 0.85), 2),
                    "description": f"Вырубка леса в {country}",
                    "date": "2024-01-10"
                }
            ]
        }
    else:
        return {
            "country": country,
            "found": False,
            "message": f"Используйте: {', '.join(country_data.keys())}"
        }

@app.get("/api/global/fires")
async def get_fire_stats(country: str = Query(None)):
    fire_data = {
        "global": {"total": 238, "by_year": {"2020": 45, "2021": 52, "2022": 67, "2023": 74}},
        "Россия": {"total": 42, "by_year": {"2020": 8, "2021": 10, "2022": 12, "2023": 12}},
        "Германия": {"total": 18, "by_year": {"2020": 3, "2021": 4, "2022": 5, "2023": 6}},
        "Испания": {"total": 35, "by_year": {"2020": 6, "2021": 8, "2022": 10, "2023": 11}},
        "США": {"total": 87, "by_year": {"2020": 16, "2021": 18, "2022": 24, "2023": 29}}
    }
    
    if country and country in fire_data:
        return {"country": country, "data": fire_data[country]}
    else:
        return {"global": fire_data["global"], "available_countries": list(fire_data.keys())[1:]}

# Основные роуты
@app.get("/")
async def root():
    return {
        "message": "Geo Anomaly Detection System",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "api": "/docs",
            "interface": "/static/",
            "global_search": "/api/global/countries"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/test")
async def test():
    return {"test": "success", "message": "Все системы работают"}

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 GEO ANOMALY DETECTOR - СИСТЕМА ЗАПУЩЕНА!")
    print("="*70)
    print("👉 ОСНОВНЫЕ ССЫЛКИ:")
    print("   • Интерфейс:        http://localhost:8000/static/")
    print("   • API Документация: http://localhost:8000/docs")
    print("   • Глобальный поиск: http://localhost:8000/api/global/countries")
    print("\n🎯 ФУНКЦИОНАЛЬНОСТЬ:")
    print("   • Загрузка изображений ✓")
    print("   • Поиск по странам ✓")
    print("   • Статистика пожаров ✓")
    print("   • Интерактивная карта ✓")
    print("="*70)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)