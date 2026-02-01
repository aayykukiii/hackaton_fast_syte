import numpy as np
import cv2
from typing import Tuple

def normalize_image(image: np.ndarray) -> np.ndarray:
    """Нормализация изображения"""
    return (image - image.min()) / (image.max() - image.min() + 1e-7)

def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """Изменение размера изображения"""
    return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

def apply_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """Вычисление NDVI (Normalized Difference Vegetation Index)"""
    ndvi = (nir_band - red_band) / (nir_band + red_band + 1e-7)
    return np.clip(ndvi, -1, 1)