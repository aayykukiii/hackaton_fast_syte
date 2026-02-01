import numpy as np
from typing import Tuple, Dict
import random

class AnomalyClassifier:
    def __init__(self):
        self.classes = ['fire', 'deforestation', 'dump', 'construction', 'flood', 'normal']
    
    def classify(self, image: np.ndarray, region: Dict) -> Tuple[str, float]:
        """Классификация региона изображения"""
        # Простая демо классификация
        anomaly_types = ['fire', 'deforestation', 'dump', 'construction', 'flood']
        
        if random.random() > 0.3:  # 70% шанс обнаружить аномалию
            anomaly_type = random.choice(anomaly_types)
            confidence = round(random.uniform(0.6, 0.95), 2)
        else:
            anomaly_type = 'normal'
            confidence = round(random.uniform(0.3, 0.6), 2)
        
        return anomaly_type, confidence