import cv2
import numpy as np
from typing import Tuple, List, Dict

class ChangeDetector:
    def __init__(self, threshold: int = 30, min_area: int = 100):
        self.threshold = threshold
        self.min_area = min_area
    
    def detect_changes(self, image1: np.ndarray, image2: np.ndarray) -> np.ndarray:
        """Обнаружение изменений между изображениями"""
        if image1.shape != image2.shape:
            height = min(image1.shape[0], image2.shape[0])
            width = min(image1.shape[1], image2.shape[1])
            image1 = cv2.resize(image1, (width, height))
            image2 = cv2.resize(image2, (width, height))
        
        gray1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
        
        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
        
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return thresh
    
    def find_anomaly_regions(self, change_mask: np.ndarray) -> List[Dict]:
        """Поиск регионов с аномалиями"""
        contours, _ = cv2.findContours(
            change_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area:
                x, y, w, h = cv2.boundingRect(contour)
                regions.append({
                    'bbox': (x, y, x + w, y + h),
                    'area': area,
                    'center': (x + w // 2, y + h // 2)
                })
        
        return regions