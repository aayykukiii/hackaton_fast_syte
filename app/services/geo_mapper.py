class GeoMapper:
    def __init__(self, image_size: tuple = (1920, 1080), 
                 geo_bounds: tuple = (55.0, 37.0, 56.0, 38.0)):
        self.image_width, self.image_height = image_size
        self.lat_min, self.lon_min, self.lat_max, self.lon_max = geo_bounds
    
    def pixel_to_geo(self, x: float, y: float) -> tuple:
        """Преобразование пикселей в географические координаты"""
        x_norm = x / self.image_width
        y_norm = y / self.image_height
        
        lon = self.lon_min + x_norm * (self.lon_max - self.lon_min)
        lat = self.lat_min + (1 - y_norm) * (self.lat_max - self.lat_min)
        
        return round(lat, 6), round(lon, 6)
    
    def geo_to_pixel(self, lat: float, lon: float) -> tuple:
        """Преобразование географических координат в пиксели"""
        x_norm = (lon - self.lon_min) / (self.lon_max - self.lon_min)
        y_norm = 1 - (lat - self.lat_min) / (self.lat_max - self.lat_min)
        
        x = x_norm * self.image_width
        y = y_norm * self.image_height
        
        return x, y