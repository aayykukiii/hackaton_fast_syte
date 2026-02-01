import os
from typing import Optional

class Settings:
    DATABASE_URL: str = "sqlite:///geo_anomaly.db"
    SECRET_KEY: str = "hakaton-secret-key-2024"
    DEBUG: bool = True
    
    def __init__(self):
        # Можно переопределить через .env
        if os.path.exists(".env"):
            from dotenv import load_dotenv
            load_dotenv()
            
            self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
            self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
            self.DEBUG = os.getenv("DEBUG", str(self.DEBUG)).lower() == "true"

settings = Settings()