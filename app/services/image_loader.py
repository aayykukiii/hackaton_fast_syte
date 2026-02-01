import cv2
import numpy as np
from PIL import Image
import os
from typing import Optional, Dict

class ImageLoader:
    @staticmethod
    def load_image(filepath: str) -> Optional[np.ndarray]:
        """Загрузка изображения"""
        if not os.path.exists(filepath):
            return None
        
        try:
            image = cv2.imread(filepath)
            if image is not None:
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return None
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    @staticmethod
    def get_image_metadata(filepath: str) -> Dict:
        """Получение метаданных изображения"""
        try:
            with Image.open(filepath) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
        except Exception as e:
            print(f"Error reading metadata: {e}")
            return {'width': 1920, 'height': 1080, 'format': 'unknown'}