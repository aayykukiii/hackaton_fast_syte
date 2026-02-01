import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class GlobalAnomalyDatabase:
    """Глобальная база данных аномалий по всему миру"""
    
    def __init__(self):
        self.countries = {
            'Россия': {
                'capital': 'Москва',
                'coords': (55.7558, 37.6173),
                'regions': ['Москва', 'Санкт-Петербург', 'Сибирь', 'Дальний Восток']
            },
            'Германия': {
                'capital': 'Берлин', 
                'coords': (52.5200, 13.4050),
                'regions': ['Бавария', 'Баден-Вюртемберг', 'Северный Рейн-Вестфалия']
            },
            'Испания': {
                'capital': 'Мадрид',
                'coords': (40.4168, -3.7038),
                'regions': ['Андалусия', 'Каталония', 'Валенсия', 'Галисия']
            },
            'США': {
                'capital': 'Вашингтон',
                'coords': (38.9072, -77.0369),
                'regions': ['Калифорния', 'Техас', 'Флорида', 'Аляска']
            },
            'Бразилия': {
                'capital': 'Бразилиа',
                'coords': (-15.7975, -47.8919),
                'regions': ['Амазонас', 'Сан-Паулу', 'Рио-де-Жанейро']
            },
            'Китай': {
                'capital': 'Пекин',
                'coords': (39.9042, 116.4074),
                'regions': ['Шанхай', 'Гуандун', 'Синьцзян']
            },
            'Австралия': {
                'capital': 'Канберра',
                'coords': (-35.2809, 149.1300),
                'regions': ['Новый Южный Уэльс', 'Квинсленд', 'Западная Австралия']
            }
        }
        
        # Создаем исторические данные
        self.historical_data = self._generate_historical_data()
    
    def _generate_historical_data(self) -> List[Dict]:
        """Генерация исторических данных аномалий"""
        data = []
        anomaly_id = 1
        
        # Годы для генерации
        years = [2020, 2021, 2022, 2023, 2024]
        
        for country_name, country_info in self.countries.items():
            for year in years:
                for month in range(1, 13):
                    # Количество аномалий в месяц (случайное)
                    monthly_anomalies = random.randint(2, 10)
                    
                    for _ in range(monthly_anomalies):
                        # Случайный день месяца
                        day = random.randint(1, 28)
                        date = datetime(year, month, day)
                        
                        # Случайный тип аномалии
                        anomaly_type = random.choice(['fire', 'deforestation', 'dump', 'construction', 'flood'])
                        
                        # Координаты в пределах страны
                        base_lat, base_lng = country_info['coords']
                        lat = base_lat + random.uniform(-5, 5)
                        lng = base_lng + random.uniform(-5, 5)
                        
                        # Уверенность
                        confidence = round(random.uniform(0.5, 0.95), 2)
                        
                        # Описание
                        descriptions = {
                            'fire': [
                                f'Лесной пожар в {country_name}, площадь {random.randint(10, 500)} га',
                                f'Торфяной пожар в регионе {random.choice(country_info["regions"])}',
                                f'Пожар на сельхозугодьях в {country_name}'
                            ],
                            'deforestation': [
                                f'Незаконная вырубка леса в {country_name}',
                                f'Расчистка территории под строительство в {random.choice(country_info["regions"])}',
                                f'Вырубка леса для сельского хозяйства'
                            ],
                            'dump': [
                                f'Несанкционированная свалка в {country_name}',
                                f'Скопление мусора в регионе {random.choice(country_info["regions"])}',
                                f'Загрязнение территории отходами'
                            ],
                            'construction': [
                                f'Незаконное строительство в {country_name}',
                                f'Строительные работы в охраняемой зоне',
                                f'Изменение ландшафта под застройку'
                            ],
                            'flood': [
                                f'Затопление территории в {country_name}',
                                f'Паводок в регионе {random.choice(country_info["regions"])}',
                                f'Подтопление сельхозугодий'
                            ]
                        }
                        
                        description = random.choice(descriptions[anomaly_type])
                        
                        data.append({
                            'id': anomaly_id,
                            'country': country_name,
                            'region': random.choice(country_info['regions']),
                            'anomaly_type': anomaly_type,
                            'latitude': lat,
                            'longitude': lng,
                            'confidence': confidence,
                            'description': description,
                            'date': date.strftime('%Y-%m-%d'),
                            'year': year,
                            'month': month,
                            'day': day,
                            'area_ha': random.randint(1, 1000),
                            'severity': random.choice(['low', 'medium', 'high']),
                            'status': random.choice(['active', 'resolved', 'monitoring'])
                        })
                        
                        anomaly_id += 1
        
        return data
    
    def search_by_country(self, country: str, year: Optional[int] = None) -> List[Dict]:
        """Поиск аномалий по стране"""
        results = [d for d in self.historical_data if d['country'].lower() == country.lower()]
        
        if year:
            results = [d for d in results if d['year'] == year]
        
        return results
    
    def search_by_coordinates(self, lat: float, lng: float, radius_km: float = 100) -> List[Dict]:
        """Поиск аномалий по координатам"""
        results = []
        
        for anomaly in self.historical_data:
            # Простое вычисление расстояния
            lat_diff = abs(anomaly['latitude'] - lat)
            lng_diff = abs(anomaly['longitude'] - lng)
            
            # Примерная проверка (1 градус ≈ 111 км)
            if lat_diff * 111 < radius_km and lng_diff * 111 < radius_km:
                results.append(anomaly)
        
        return results
    
    def get_country_stats(self, country: str) -> Dict:
        """Статистика по стране"""
        country_data = self.search_by_country(country)
        
        if not country_data:
            return {}
        
        # Группировка по годам
        by_year = {}
        for item in country_data:
            year = item['year']
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(item)
        
        # Группировка по типам
        by_type = {}
        for item in country_data:
            anomaly_type = item['anomaly_type']
            if anomaly_type not in by_type:
                by_type[anomaly_type] = 0
            by_type[anomaly_type] += 1
        
        # Общая статистика
        total = len(country_data)
        current_year = datetime.now().year
        this_year = len([d for d in country_data if d['year'] == current_year])
        
        return {
            'country': country,
            'total_anomalies': total,
            'this_year': this_year,
            'by_year': {year: len(data) for year, data in by_year.items()},
            'by_type': by_type,
            'first_record': min([d['date'] for d in country_data]),
            'last_record': max([d['date'] for d in country_data]),
            'avg_confidence': round(sum(d['confidence'] for d in country_data) / total, 2),
            'total_area_ha': sum(d['area_ha'] for d in country_data)
        }
    
    def get_time_range_stats(self, start_date: str, end_date: str) -> Dict:
        """Статистика за период времени"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        period_data = []
        for anomaly in self.historical_data:
            anomaly_date = datetime.strptime(anomaly['date'], '%Y-%m-%d')
            if start <= anomaly_date <= end:
                period_data.append(anomaly)
        
        # Группировка по странам
        by_country = {}
        for item in period_data:
            country = item['country']
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(item)
        
        # Группировка по типам
        by_type = {}
        for item in period_data:
            anomaly_type = item['anomaly_type']
            if anomaly_type not in by_type:
                by_type[anomaly_type] = 0
            by_type[anomaly_type] += 1
        
        return {
            'period': f'{start_date} to {end_date}',
            'total_anomalies': len(period_data),
            'by_country': {country: len(data) for country, data in by_country.items()},
            'by_type': by_type,
            'countries_affected': len(by_country),
            'total_area_ha': sum(d['area_ha'] for d in period_data),
            'daily_avg': round(len(period_data) / ((end - start).days + 1), 2)
        }
    
    def get_fire_stats(self, country: Optional[str] = None) -> Dict:
        """Статистика пожаров"""
        fires = [d for d in self.historical_data if d['anomaly_type'] == 'fire']
        
        if country:
            fires = [d for d in fires if d['country'].lower() == country.lower()]
        
        if not fires:
            return {}
        
        # Группировка по годам
        by_year = {}
        for fire in fires:
            year = fire['year']
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(fire)
        
        # Самые крупные пожары
        largest_fires = sorted(fires, key=lambda x: x['area_ha'], reverse=True)[:5]
        
        return {
            'total_fires': len(fires),
            'total_area_ha': sum(f['area_ha'] for f in fires),
            'avg_fire_size': round(sum(f['area_ha'] for f in fires) / len(fires), 1),
            'by_year': {year: len(data) for year, data in by_year.items()},
            'largest_fires': [
                {
                    'country': f['country'],
                    'region': f['region'],
                    'date': f['date'],
                    'area_ha': f['area_ha'],
                    'description': f['description']
                }
                for f in largest_fires
            ],
            'countries': list(set([f['country'] for f in fires]))
        }
    
    def get_recent_anomalies(self, days: int = 7) -> List[Dict]:
        """Последние аномалии"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = []
        for anomaly in self.historical_data:
            anomaly_date = datetime.strptime(anomaly['date'], '%Y-%m-%d')
            if anomaly_date >= cutoff_date:
                recent.append(anomaly)
        
        return recent
    
    def get_country_list(self) -> List[str]:
        """Список доступных стран"""
        return list(self.countries.keys())

# Глобальный экземпляр
global_db = GlobalAnomalyDatabase()