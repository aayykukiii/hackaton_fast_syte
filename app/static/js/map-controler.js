// map-controller.js
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация карты
    initMap();
    initControls();
    hideLoadingScreen();
});

let map;
let satelliteLayer;
let streetLayer;

function initMap() {
    console.log('Initializing map...');
    
    // Проверяем, существует ли элемент карты
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.error('Map element not found!');
        return;
    }
    
    // Инициализация карты с центром на Москве
    map = L.map('map', {
        center: [55.7558, 37.6173],
        zoom: 5,
        zoomControl: false,
        attributionControl: false,
        fadeAnimation: true,
        zoomAnimation: true
    });
    
    // Добавляем базовые слои
    streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    });
    
    // Спутниковый слой (NASA Blue Marble)
    satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '© Esri, NASA, NGA, USGS',
        maxZoom: 19
    }).addTo(map);
    
    // Добавляем контроль масштаба
    L.control.scale({
        imperial: false,
        metric: true,
        position: 'bottomleft'
    }).addTo(map);
    
    // Обновляем размер карты
    setTimeout(() => {
        map.invalidateSize();
        updateCoordinates();
    }, 100);
    
    // Следим за движением карты
    map.on('move', updateCoordinates);
    map.on('zoom', updateZoom);
    map.on('locationfound', onLocationFound);
    
    console.log('Map initialized successfully');
}

function initControls() {
    // Кнопки зума
    document.getElementById('zoomIn').addEventListener('click', () => map.zoomIn());
    document.getElementById('zoomOut').addEventListener('click', () => map.zoomOut());
    document.getElementById('resetView').addEventListener('click', () => {
        map.setView([55.7558, 37.6173], 5);
    });
    
    // Поиск
    const searchInput = document.getElementById('searchLocation');
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchLocation(searchInput.value);
        }
    });
    
    // Моё местоположение
    document.getElementById('locateMe').addEventListener('click', () => {
        map.locate({setView: true, maxZoom: 16});
    });
    
    // Обновление времени
    updateDateTime();
    setInterval(updateDateTime, 1000);
}

function updateCoordinates() {
    const center = map.getCenter();
    document.getElementById('latitude').textContent = center.lat.toFixed(4) + '°';
    document.getElementById('longitude').textContent = center.lng.toFixed(4) + '°';
    
    // Для примера - случайная высота
    document.getElementById('altitude').textContent = Math.floor(Math.random() * 1000) + ' м';
    
    // Масштаб
    const zoom = map.getZoom();
    const scales = {
        1: '1:500M',
        2: '1:250M',
        3: '1:100M',
        4: '1:50M',
        5: '1:25M',
        6: '1:10M',
        7: '1:5M',
        8: '1:2M',
        9: '1:1M',
        10: '1:500k',
        11: '1:250k',
        12: '1:100k',
        13: '1:50k',
        14: '1:25k',
        15: '1:10k',
        16: '1:5k',
        17: '1:2k',
        18: '1:1k',
        19: '1:500'
    };
    document.getElementById('scale').textContent = scales[zoom] || '--';
}

function updateZoom() {
    document.getElementById('zoomLevel').textContent = map.getZoom();
}

function onLocationFound(e) {
    const radius = e.accuracy / 2;
    
    L.marker(e.latlng).addTo(map)
        .bindPopup("Вы находитесь в пределах " + radius + " метров от этой точки").openPopup();
    
    L.circle(e.latlng, radius).addTo(map);
}

function searchLocation(query) {
    if (!query.trim()) return;
    
    // Используем Nominatim для поиска
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lon = parseFloat(result.lon);
                
                map.setView([lat, lon], 14);
                
                // Добавляем маркер
                L.marker([lat, lon])
                    .addTo(map)
                    .bindPopup(`<b>${result.display_name}</b>`)
                    .openPopup();
            } else {
                alert('Местоположение не найдено');
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            alert('Ошибка при поиске');
        });
}

function updateDateTime() {
    const now = new Date();
    
    // Время
    const time = now.toLocaleTimeString('ru-RU');
    document.getElementById('currentTime').textContent = time;
    
    // Дата
    const date = now.toLocaleDateString('ru-RU', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    document.getElementById('currentDate').textContent = date;
}

function hideLoadingScreen() {
    // Симуляция загрузки
    let progress = 0;
    const progressBar = document.getElementById('loadingProgress');
    const percentElement = document.getElementById('loadingPercent');
    const statusElement = document.getElementById('loadingStatus');
    
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 100) {
            progress = 100;
            clearInterval(interval);
            
            // Скрываем экран загрузки
            setTimeout(() => {
                document.getElementById('loadingScreen').style.opacity = '0';
                setTimeout(() => {
                    document.getElementById('loadingScreen').style.display = 'none';
                }, 500);
            }, 500);
        }
        
        progressBar.style.width = progress + '%';
        percentElement.textContent = Math.round(progress) + '%';
        
        // Обновляем статусы
        if (progress < 30) {
            statusElement.textContent = 'Загрузка спутниковых данных...';
        } else if (progress < 60) {
            statusElement.textContent = 'Подключение к серверам...';
        } else if (progress < 90) {
            statusElement.textContent = 'Инициализация карты...';
        } else {
            statusElement.textContent = 'Завершение инициализации...';
        }
        
        // Обновляем статистику загрузки
        document.getElementById('satConnections').textContent = 
            Math.min(12, Math.floor(progress / 8.3)) + '/12';
        document.getElementById('tileProgress').textContent = Math.round(progress) + '%';
        
    }, 100);
}

// Глобальные функции для кнопок
window.toggleSatellite = function() {
    if (map.hasLayer(satelliteLayer)) {
        map.removeLayer(satelliteLayer);
        streetLayer.addTo(map);
    } else {
        map.removeLayer(streetLayer);
        satelliteLayer.addTo(map);
    }
};

window.exportMap = function() {
    // Здесь будет код для экспорта карты
    alert('Экспорт карты в разработке');
};