import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime
import os

from .image_loader import ImageLoader
from .change_detect import ChangeDetector
from .classifier import AnomalyClassifier
from .geo_mapper import GeoMapper

class ImageAnalyzer:
    """Основной сервис анализа изображений"""
    
    def __init__(self):
        self.image_loader = ImageLoader()
        self.change_detector = ChangeDetector(threshold=25, min_area=50)
        self.classifier = AnomalyClassifier()
        self.results_cache = {}
    
    def analyze_single_image(self, 
                           image_path: str,
                           reference_path: Optional[str] = None) -> Dict:
        """
        Анализ одного изображения или сравнение с референсным
        
        Returns:
            Словарь с результатами анализа
        """
        # Загружаем основное изображение
        image = self.image_loader.load_image(image_path)
        if image is None:
            return {"error": "Failed to load image"}
        
        # Получаем метаданные
        metadata = self.image_loader.get_image_metadata(image_path)
        
        # Создаем геомаппер
        geo_mapper = GeoMapper.create_from_metadata(metadata)
        
        results = {
            "image_info": {
                "path": image_path,
                "size": image.shape[:2],
                "metadata": metadata
            },
            "timestamp": datetime.now().isoformat(),
            "anomalies": []
        }
        
        if reference_path:
            # Сравнение с референсным изображением
            reference_image = self.image_loader.load_image(reference_path)
            if reference_image is not None:
                # Обнаружение изменений
                change_mask = self.change_detector.detect_changes(
                    reference_image, image, method='simple'
                )
                
                # Нахождение регионов изменений
                regions = self.change_detector.find_anomaly_regions(change_mask)
                
                # Классификация каждого региона
                for region in regions:
                    anomaly_type, confidence = self.classifier.classify(image, region)
                    
                    # Пропускаем нормальные регионы с низкой уверенностью
                    if anomaly_type == "normal" and confidence < 0.5:
                        continue
                    
                    # Преобразуем координаты в географические
                    center_x, center_y = region['center']
                    latitude, longitude = geo_mapper.pixel_to_geo(center_x, center_y)
                    
                    anomaly = {
                        "type": anomaly_type,
                        "confidence": float(confidence),
                        "location": {
                            "latitude": latitude,
                            "longitude": longitude,
                            "pixel_center": region['center'],
                            "bbox": region['bbox']
                        },
                        "area": float(region['area']),
                        "bbox_geo": geo_mapper.bbox_to_geo(region['bbox']),
                        "description": self._generate_description(anomaly_type, confidence)
                    }
                    
                    results["anomalies"].append(anomaly)
                
                # Визуализация результатов
                visualization = self.change_detector.visualize_changes(
                    image, change_mask, regions
                )
                
                # Сохраняем визуализацию
                vis_filename = f"visualization_{os.path.basename(image_path)}"
                vis_path = self.image_loader.save_processed_image(visualization, vis_filename)
                results["visualization_path"] = vis_path
                
                results["change_statistics"] = {
                    "total_changes": len(regions),
                    "change_area": float(np.sum(change_mask > 0)),
                    "change_percentage": float(np.sum(change_mask > 0) / change_mask.size * 100)
                }
        
        else:
            # Анализ одного изображения (поиск аномалий без сравнения)
            # Здесь можно добавить анализ по абсолютным признакам
            # Например, поиск областей с необычным цветом или текстурой
            
            # Простой детектор по цвету
            color_anomalies = self._detect_color_anomalies(image)
            
            for anomaly in color_anomalies:
                anomaly_type, confidence, bbox = anomaly
                center_x = (bbox[0] + bbox[2]) // 2
                center_y = (bbox[1] + bbox[3]) // 2
                
                latitude, longitude = geo_mapper.pixel_to_geo(center_x, center_y)
                
                results["anomalies"].append({
                    "type": anomaly_type,
                    "confidence": float(confidence),
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "pixel_center": (center_x, center_y),
                        "bbox": bbox
                    },
                    "area": float((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])),
                    "bbox_geo": geo_mapper.bbox_to_geo(bbox),
                    "description": self._generate_description(anomaly_type, confidence)
                })
        
        return results
    
    def _detect_color_anomalies(self, image: np.ndarray) -> List[Tuple]:
        """Обнаружение аномалий по цвету (без сравнения)"""
        anomalies = []
        height, width = image.shape[:2]
        
        # Разбиваем изображение на сетку
        grid_size = 8
        cell_height = height // grid_size
        cell_width = width // grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                y1 = i * cell_height
                y2 = (i + 1) * cell_height
                x1 = j * cell_width
                x2 = (j + 1) * cell_width
                
                # Извлекаем ячейку
                cell = image[y1:y2, x1:x2]
                if cell.size == 0:
                    continue
                
                # Анализируем средний цвет
                mean_color = np.mean(cell, axis=(0, 1))
                
                # Простые правила для демо
                # Красный канал сильно выделяется -> возможный пожар
                if mean_color[0] > mean_color[1] * 1.5 and mean_color[0] > mean_color[2] * 1.5:
                    anomalies.append(("fire", 0.6, (x1, y1, x2, y2)))
                
                # Коричневые/серые тона -> возможная вырубка/свалка
                elif mean_color[0] > 100 and mean_color[1] < 100 and mean_color[2] < 100:
                    anomalies.append(("deforestation", 0.5, (x1, y1, x2, y2)))
        
        return anomalies
    
    def _generate_description(self, anomaly_type: str, confidence: float) -> str:
        """Генерация описания аномалии"""
        descriptions = {
            "fire": [
                "Обнаружена тепловая аномалия, возможный очаг пожара",
                "Высокая температура в области, вероятен лесной пожар",
                "Термическая активность обнаружена"
            ],
            "deforestation": [
                "Обнаружена вырубка леса",
                "Изменение растительного покрова, возможная вырубка",
                "Участок с удаленной растительностью"
            ],
            "dump": [
                "Обнаружена несанкционированная свалка",
                "Скопление посторонних объектов на территории",
                "Аномалия, похожая на свалку отходов"
            ],
            "construction": [
                "Обнаружена строительная активность",
                "Новые сооружения или изменения рельефа",
                "Антропогенные изменения ландшафта"
            ],
            "flood": [
                "Обнаружено затопление территории",
                "Аномальное скопление воды",
                "Изменение водного покрова"
            ]
        }
        
        if anomaly_type in descriptions:
            desc_list = descriptions[anomaly_type]
            idx = min(int(confidence * 10) % len(desc_list), len(desc_list) - 1)
            base_desc = desc_list[idx]
        else:
            base_desc = f"Обнаружена аномалия типа '{anomaly_type}'"
        
        confidence_percent = int(confidence * 100)
        return f"{base_desc} (уверенность: {confidence_percent}%)"
    
    def batch_analyze(self, image_paths: List[str]) -> Dict:
        """Пакетный анализ нескольких изображений"""
        results = {
            "total_images": len(image_paths),
            "analyzed_images": 0,
            "total_anomalies": 0,
            "anomalies_by_type": {},
            "results": []
        }
        
        for image_path in image_paths:
            try:
                analysis_result = self.analyze_single_image(image_path)
                results["results"].append(analysis_result)
                results["analyzed_images"] += 1
                
                # Статистика по аномалиям
                for anomaly in analysis_result.get("anomalies", []):
                    results["total_anomalies"] += 1
                    anomaly_type = anomaly["type"]
                    if anomaly_type not in results["anomalies_by_type"]:
                        results["anomalies_by_type"][anomaly_type] = 0
                    results["anomalies_by_type"][anomaly_type] += 1
                    
            except Exception as e:
                print(f"Error analyzing {image_path}: {e}")
                continue
        
        return results               