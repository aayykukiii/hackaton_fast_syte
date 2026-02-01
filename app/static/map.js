/**
 * Geo Anomaly Detector - Основной файл JavaScript
 * Усовершенствованная версия с улучшенной архитектурой
 */

// Основные константы и переменные
const AppConfig = {
    MAP_CENTER: [55.7558, 37.6173],
    MAP_ZOOM: 5,
    AUTO_REFRESH_INTERVAL: 60000, // 60 секунд
    DEFAULT_CONFIDENCE: 50,
    API_BASE_URL: '/api',
    MAX_ANOMALIES_PER_LOAD: 100
};

class GeoAnomalyDetector {
    constructor() {
        this.map = null;
        this.anomalyMarkers = new Map();
        this.heatmapLayer = null;
        this.clusterLayer = null;
        this.currentFilters = {
            anomalyType: '',
            minConfidence: AppConfig.DEFAULT_CONFIDENCE / 100,
            region: '',
            dateRange: {
                start: null,
                end: null
            }
        };
        this.isLoading = false;
        this.anomalies = [];
        
        this.init();
    }

    // Инициализация приложения
    async init() {
        try {
            await this.initMap();
            this.initEventListeners();
            this.initUIComponents();
            await this.loadInitialData();
            this.startAutoRefresh();
            
            this.showNotification('Система мониторинга инициализирована', 'success');
        } catch (error) {
            console.error('Ошибка инициализации:', error);
            this.showNotification('Ошибка инициализации системы', 'error');
        }
    }

    // Инициализация карты
    initMap() {
        return new Promise((resolve) => {
            this.map = L.map('map', {
                center: AppConfig.MAP_CENTER,
                zoom: AppConfig.MAP_ZOOM,
                zoomControl: false,
                preferCanvas: true,
                maxZoom: 19,
                minZoom: 3
            });

            // Базовый слой OpenStreetMap
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19,
                detectRetina: true
            }).addTo(this.map);

            // Спутниковый слой (скрыт по умолчанию)
            this.satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© Esri, Maxar, Earthstar Geographics',
                maxZoom: 19,
                detectRetina: true
            });

            // Создаем группу для маркеров с кластеризацией
            this.clusterLayer = L.markerClusterGroup({
                maxClusterRadius: 50,
                iconCreateFunction: this.createClusterIcon.bind(this),
                showCoverageOnHover: false,
                zoomToBoundsOnClick: true,
                spiderfyOnMaxZoom: true
            });
            this.map.addLayer(this.clusterLayer);

            // Слой для тепловой карты
            this.heatmapLayer = L.layerGroup();
            this.map.addLayer(this.heatmapLayer);

            // Добавляем контролы
            this.initMapControls();
            
            resolve();
        });
    }

    // Создание иконки для кластера
    createClusterIcon(cluster) {
        const count = cluster.getChildCount();
        let className = 'cluster-marker';
        let size = 40;
        
        if (count > 50) {
            className += ' cluster-large';
            size = 50;
        } else if (count > 10) {
            className += ' cluster-medium';
            size = 45;
        }
        
        return L.divIcon({
            html: `<div class="cluster-content"><span>${count}</span></div>`,
            iconSize: [size, size],
            className: className
        });
    }

    // Инициализация контролов карты
    initMapControls() {
        // Пользовательские контролы
        L.control.zoom({
            position: 'bottomright'
        }).addTo(this.map);

        // Контрол слоев
        const baseLayers = {
            "Карта улиц": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
            "Спутник": this.satelliteLayer
        };

        const overlayLayers = {
            "Тепловая карта": this.heatmapLayer,
            "Маркеры аномалий": this.clusterLayer
        };

        L.control.layers(baseLayers, overlayLayers, {
            position: 'topright',
            collapsed: true
        }).addTo(this.map);
    }

    // Инициализация слушателей событий
    initEventListeners() {
        // Слайдер уверенности
        const confidenceSlider = document.getElementById('confidence');
        const confidenceValue = document.getElementById('confidenceValue');
        
        confidenceSlider.addEventListener('input', (e) => {
            const value = e.target.value;
            confidenceValue.textContent = `${value}%`;
            this.currentFilters.minConfidence = value / 100;
            this.debouncedFilterAnomalies();
        });

        // Фильтры
        document.getElementById('anomalyType').addEventListener('change', (e) => {
            this.currentFilters.anomalyType = e.target.value;
            this.debouncedFilterAnomalies();
        });

        document.getElementById('regionSelect').addEventListener('change', (e) => {
            this.currentFilters.region = e.target.value;
            this.debouncedFilterAnomalies();
        });

        // Даты
        document.getElementById('startDate').addEventListener('change', (e) => {
            this.currentFilters.dateRange.start = e.target.value;
            this.debouncedFilterAnomalies();
        });

        document.getElementById('endDate').addEventListener('change', (e) => {
            this.currentFilters.dateRange.end = e.target.value;
            this.debouncedFilterAnomalies();
        });

        // Кнопки действий
        document.querySelector('.btn-primary').addEventListener('click', () => this.loadAnomalies());
        document.querySelector('.btn-success').addEventListener('click', () => this.runRealTimeTest());
        document.querySelector('.btn-export').addEventListener('click', () => this.exportData());

        // Управление картой
        document.querySelector('[onclick*="zoomIn"]')?.addEventListener('click', () => this.map.zoomIn());
        document.querySelector('[onclick*="zoomOut"]')?.addEventListener('click', () => this.map.zoomOut());
        document.querySelector('[onclick*="resetView"]')?.addEventListener('click', () => this.resetMapView());
        document.querySelector('[onclick*="toggleSatellite"]')?.addEventListener('click', () => this.toggleMapLayer());

        // Ресайз окна
        window.addEventListener('resize', () => this.debouncedResizeMap());
    }

    // Debounce для фильтрации
    debouncedFilterAnomalies = this.debounce(() => {
        this.filterAnomalies();
    }, 300);

    // Debounce для ресайза
    debouncedResizeMap = this.debounce(() => {
        this.map.invalidateSize();
    }, 150);

    // Утилита debounce
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Инициализация UI компонентов
    initUIComponents() {
        // Инициализация датапикеров
        const today = new Date();
        const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        document.getElementById('startDate').value = lastWeek.toISOString().split('T')[0];
        document.getElementById('endDate').value = today.toISOString().split('T')[0];

        // Обновление времени
        this.updateTime();
        setInterval(() => this.updateTime(), 60000);
    }

    // Обновление времени
    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ru-RU', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        document.getElementById('lastUpdateTime').textContent = timeString;
    }

    // Загрузка начальных данных
    async loadInitialData() {
        this.showLoading(true);
        try {
            await this.loadAnomalies();
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            await this.loadDemoData();
        } finally {
            this.showLoading(false);
        }
    }

    // Загрузка аномалий
    async loadAnomalies(forceRefresh = false) {
        if (this.isLoading && !forceRefresh) return;
        
        this.isLoading = true;
        this.showLoading(true);

        try {
            // В реальном приложении здесь был бы fetch запрос
            // Для демо используем тестовые данные
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            this.anomalies = this.generateDemoData();
            
            // Обновляем UI
            this.updateAnomalyMarkers();
            this.updateAnomalyList();
            this.updateStatistics();
            
            this.showNotification(`Загружено ${this.anomalies.length} аномалий`, 'success');
            
        } catch (error) {
            console.error('Ошибка загрузки аномалий:', error);
            this.showNotification('Ошибка загрузки данных. Используются демо-данные', 'warning');
            await this.loadDemoData();
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }

    // Загрузка демо-данных
    async loadDemoData() {
        // Генерация демо-данных
        const demoAnomalies = this.generateDemoData();
        this.anomalies = demoAnomalies;
        
        this.updateAnomalyMarkers();
        this.updateAnomalyList();
        this.updateStatistics();
    }

    // Генерация демо-данных
    generateDemoData() {
        const anomalyTypes = ['fire', 'deforestation', 'dump', 'construction', 'flood'];
        const regions = ['europe', 'asia', 'russia'];
        const demoAnomalies = [];

        for (let i = 0; i < 25; i++) {
            const type = anomalyTypes[Math.floor(Math.random() * anomalyTypes.length)];
            const confidence = Math.floor(Math.random() * 40) + 60; // 60-100%
            
            // Генерация случайных координат в пределах России
            const lat = 45 + Math.random() * 20; // 45-65 градусов северной широты
            const lng = 30 + Math.random() * 80; // 30-110 градусов восточной долготы
            
            demoAnomalies.push({
                id: `demo_${i + 1}`,
                type: type,
                title: this.getAnomalyTitle(type),
                confidence: confidence / 100,
                latitude: lat,
                longitude: lng,
                detected_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
                description: this.getAnomalyDescription(type),
                severity: confidence > 80 ? 'high' : confidence > 60 ? 'medium' : 'low',
                region: regions[Math.floor(Math.random() * regions.length)],
                area: `${Math.floor(Math.random() * 50) + 5} га`
            });
        }

        return demoAnomalies;
    }

    // Получение заголовка аномалии
    getAnomalyTitle(type) {
        const titles = {
            'fire': 'Лесной пожар',
            'deforestation': 'Незаконная вырубка',
            'dump': 'Несанкционированная свалка',
            'construction': 'Новое строительство',
            'flood': 'Затопление территории'
        };
        return titles[type] || 'Обнаружена аномалия';
    }

    // Получение описания аномалии
    getAnomalyDescription(type) {
        const descriptions = {
            'fire': 'Обнаружены признаки лесного пожара. Требуется срочное реагирование служб МЧС.',
            'deforestation': 'Выявлена незаконная вырубка лесного массива. Необходима проверка природоохранных органов.',
            'dump': 'Образована новая несанкционированная свалка. Требуется утилизация отходов.',
            'construction': 'Начато новое строительство без соответствующего разрешения.',
            'flood': 'Затопление сельскохозяйственных угодий. Возможны потери урожая.'
        };
        return descriptions[type] || 'Требуется дополнительное исследование области.';
    }

    // Обновление маркеров на карте
    updateAnomalyMarkers() {
        // Очищаем слои
        this.clusterLayer.clearLayers();
        this.heatmapLayer.clearLayers();
        this.anomalyMarkers.clear();

        // Фильтруем аномалии по текущим фильтрам
        const filteredAnomalies = this.filterAnomaliesByType(this.anomalies);

        // Добавляем маркеры для каждой аномалии
        filteredAnomalies.forEach(anomaly => {
            const marker = this.createAnomalyMarker(anomaly);
            this.anomalyMarkers.set(anomaly.id, marker);
            this.clusterLayer.addLayer(marker);

            // Добавляем в тепловую карту
            if (anomaly.confidence > 0.7) {
                this.addToHeatmap(anomaly);
            }
        });

        // Если есть аномалии, подгоняем карту
        if (filteredAnomalies.length > 0) {
            this.fitMapToAnomalies();
        }
    }

    // Создание маркера аномалии
    createAnomalyMarker(anomaly) {
        const icon = this.createMarkerIcon(anomaly.type, anomaly.confidence);
        const marker = L.marker([anomaly.latitude, anomaly.longitude], {
            icon: icon,
            title: anomaly.title,
            riseOnHover: true
        });

        // Добавляем попап
        marker.bindPopup(this.createPopupContent(anomaly), {
            maxWidth: 300,
            minWidth: 250,
            className: 'anomaly-popup'
        });

        // Добавляем обработчики
        marker.on('click', () => this.onMarkerClick(anomaly));

        return marker;
    }

    // Создание иконки маркера
    createMarkerIcon(type, confidence) {
        const colors = {
            'fire': '#e74c3c',
            'deforestation': '#8b4513',
            'dump': '#7f8c8d',
            'construction': '#f39c12',
            'flood': '#3498db'
        };

        const color = colors[type] || '#9b59b6';
        const size = confidence > 0.8 ? 32 : confidence > 0.6 ? 28 : 24;

        return L.divIcon({
            html: `
                <div class="anomaly-marker" data-type="${type}" style="background-color: ${color}">
                    <div class="marker-icon">
                        <i class="${this.getAnomalyIcon(type)}"></i>
                    </div>
                </div>
            `,
            iconSize: [size, size],
            iconAnchor: [size / 2, size],
            className: `anomaly-marker-${type}`
        });
    }

    // Получение иконки для типа аномалии
    getAnomalyIcon(type) {
        const icons = {
            'fire': 'fas fa-fire',
            'deforestation': 'fas fa-tree',
            'dump': 'fas fa-trash',
            'construction': 'fas fa-hard-hat',
            'flood': 'fas fa-water'
        };
        return icons[type] || 'fas fa-exclamation-triangle';
    }

    // Создание контента для попапа
    createPopupContent(anomaly) {
        const confidencePercent = Math.round(anomaly.confidence * 100);
        const date = new Date(anomaly.detected_at).toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });

        return `
            <div class="anomaly-popup-content">
                <div class="popup-header">
                    <span class="anomaly-type-badge ${anomaly.type}">
                        ${this.getAnomalyTypeName(anomaly.type)}
                    </span>
                    <span class="confidence-badge">
                        ${confidencePercent}%
                    </span>
                </div>
                
                <h4>${anomaly.title}</h4>
                
                <div class="popup-info">
                    <div class="info-row">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${anomaly.latitude.toFixed(4)}, ${anomaly.longitude.toFixed(4)}</span>
                    </div>
                    <div class="info-row">
                        <i class="far fa-calendar"></i>
                        <span>${date}</span>
                    </div>
                </div>
                
                <p class="popup-description">${anomaly.description}</p>
                
                <div class="popup-actions">
                    <button class="btn-popup" onclick="app.showAnomalyDetail('${anomaly.id}')">
                        <i class="fas fa-info-circle"></i> Подробнее
                    </button>
                </div>
            </div>
        `;
    }

    // Добавление в тепловую карту
    addToHeatmap(anomaly) {
        const intensity = anomaly.confidence;
        const radius = intensity * 1000;
        
        L.circle([anomaly.latitude, anomaly.longitude], {
            color: this.getHeatmapColor(intensity),
            fillColor: this.getHeatmapColor(intensity),
            fillOpacity: 0.1,
            radius: radius,
            weight: 1
        }).addTo(this.heatmapLayer);
    }

    // Получение цвета для тепловой карты
    getHeatmapColor(intensity) {
        if (intensity > 0.8) return '#e74c3c';
        if (intensity > 0.6) return '#f39c12';
        return '#f1c40f';
    }

    // Обработчик клика по маркеру
    onMarkerClick(anomaly) {
        // Центрируем карту на маркере
        this.map.setView([anomaly.latitude, anomaly.longitude], 12);
        
        // Выделяем карточку в списке
        this.highlightAnomalyCard(anomaly.id);
    }

    // Подгон карты к аномалиям
    fitMapToAnomalies() {
        const bounds = this.clusterLayer.getBounds();
        if (bounds.isValid()) {
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }
    }

    // Обновление списка аномалий
    updateAnomalyList() {
        const container = document.getElementById('anomalyList');
        const filteredAnomalies = this.filterAnomaliesByType(this.anomalies);

        if (filteredAnomalies.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <h4>Аномалии не найдены</h4>
                    <p>Измените параметры фильтрации или загрузите новые данные</p>
                </div>
            `;
            return;
        }

        // Сортируем по уверенности (убыванию)
        filteredAnomalies.sort((a, b) => b.confidence - a.confidence);

        container.innerHTML = filteredAnomalies.map(anomaly => 
            this.createAnomalyCard(anomaly)
        ).join('');

        // Обновляем счетчик
        document.getElementById('anomalyCount').textContent = filteredAnomalies.length;
    }

    // Создание карточки аномалии
    createAnomalyCard(anomaly) {
        const confidencePercent = Math.round(anomaly.confidence * 100);
        const date = new Date(anomaly.detected_at).toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'short'
        });

        return `
            <div class="anomaly-card ${anomaly.type}" onclick="app.showAnomalyDetail('${anomaly.id}')">
                <div class="anomaly-card-header">
                    <span class="anomaly-type-badge ${anomaly.type}">
                        ${this.getAnomalyTypeName(anomaly.type)}
                    </span>
                    <div class="confidence-indicator">
                        <span class="confidence-value">${confidencePercent}%</span>
                    </div>
                </div>
                
                <h4 class="anomaly-title">${anomaly.title}</h4>
                
                <div class="anomaly-meta">
                    <div class="meta-item">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${this.formatCoordinates(anomaly.latitude, anomaly.longitude)}</span>
                    </div>
                    <div class="meta-item">
                        <i class="far fa-calendar"></i>
                        <span>${date}</span>
                    </div>
                </div>
                
                <p class="anomaly-description">${anomaly.description.substring(0, 80)}...</p>
                
                <div class="anomaly-card-footer">
                    <div class="severity-badge severity-${anomaly.severity}">
                        ${this.getSeverityName(anomaly.severity)}
                    </div>
                    <button class="btn-card-action" onclick="event.stopPropagation(); app.zoomToAnomaly('${anomaly.id}')">
                        <i class="fas fa-search-location"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // Форматирование координат
    formatCoordinates(lat, lng) {
        return `${lat.toFixed(2)}, ${lng.toFixed(2)}`;
    }

    // Получение имени типа аномалии
    getAnomalyTypeName(type) {
        const names = {
            'fire': 'Пожар',
            'deforestation': 'Вырубка',
            'dump': 'Свалка',
            'construction': 'Строительство',
            'flood': 'Затопление'
        };
        return names[type] || 'Аномалия';
    }

    // Получение имени серьезности
    getSeverityName(severity) {
        const names = {
            'high': 'Высокий',
            'medium': 'Средний',
            'low': 'Низкий'
        };
        return names[severity] || 'Неизвестно';
    }

    // Получение имени региона
    getRegionName(region) {
        const names = {
            'europe': 'Европа',
            'asia': 'Азия',
            'russia': 'Россия'
        };
        return names[region] || 'Не указан';
    }

    // Получение цвета для уверенности
    getConfidenceColor(percent) {
        if (percent >= 80) return '#2ecc71';
        if (percent >= 60) return '#f39c12';
        return '#e74c3c';
    }

    // Фильтрация аномалий по типу
    filterAnomaliesByType(anomalies) {
        return anomalies.filter(anomaly => {
            // Фильтр по типу
            if (this.currentFilters.anomalyType && anomaly.type !== this.currentFilters.anomalyType) {
                return false;
            }
            
            // Фильтр по уверенности
            if (anomaly.confidence < this.currentFilters.minConfidence) {
                return false;
            }
            
            // Фильтр по региону
            if (this.currentFilters.region && anomaly.region !== this.currentFilters.region) {
                return false;
            }
            
            // Фильтр по дате
            if (this.currentFilters.dateRange.start) {
                const anomalyDate = new Date(anomaly.detected_at);
                const startDate = new Date(this.currentFilters.dateRange.start);
                
                if (anomalyDate < startDate) {
                    return false;
                }
            }
            
            if (this.currentFilters.dateRange.end) {
                const anomalyDate = new Date(anomaly.detected_at);
                const endDate = new Date(this.currentFilters.dateRange.end);
                endDate.setHours(23, 59, 59, 999);
                
                if (anomalyDate > endDate) {
                    return false;
                }
            }
            
            return true;
        });
    }

    // Применение фильтров
    filterAnomalies() {
        this.updateAnomalyMarkers();
        this.updateAnomalyList();
        this.updateStatistics();
    }

    // Обновление статистики
    updateStatistics() {
        const filteredAnomalies = this.filterAnomaliesByType(this.anomalies);
        const total = filteredAnomalies.length;
        
        // Сегодняшние аномалии
        const today = new Date().toDateString();
        const todayCount = filteredAnomalies.filter(a => 
            new Date(a.detected_at).toDateString() === today
        ).length;
        
        // Средняя уверенность
        const avgConfidence = total > 0
            ? Math.round(filteredAnomalies.reduce((sum, a) => sum + a.confidence, 0) / total * 100)
            : 0;
        
        // Высокий риск
        const highRiskCount = filteredAnomalies.filter(a => a.severity === 'high').length;
        
        // Обновляем UI
        document.getElementById('totalAnomalies').textContent = total;
        document.getElementById('todayAnomalies').textContent = todayCount;
        document.getElementById('avgConfidence').textContent = `${avgConfidence}%`;
        document.getElementById('highRiskCount').textContent = highRiskCount;
        
        // Обновляем легенду
        this.updateLegendCounts(filteredAnomalies);
    }

    // Обновление счетчиков в легенде
    updateLegendCounts(anomalies) {
        const types = ['fire', 'deforestation', 'dump', 'construction', 'flood'];
        types.forEach(type => {
            const count = anomalies.filter(a => a.type === type).length;
            const element = document.getElementById(`${type}Count`);
            if (element) element.textContent = count;
        });
    }

    // Запуск автообновления
    startAutoRefresh() {
        setInterval(() => {
            if (!this.isLoading) {
                this.loadAnomalies();
            }
        }, AppConfig.AUTO_REFRESH_INTERVAL);
    }

    // Тестовый анализ в реальном времени
    async runRealTimeTest() {
        this.showNotification('Запуск тестового анализа...', 'info');
        
        const originalText = document.querySelector('.btn-success').innerHTML;
        document.querySelector('.btn-success').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Анализ...';
        document.querySelector('.btn-success').disabled = true;
        
        try {
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Создаем тестовую аномалию
            const testAnomaly = this.generateTestAnomaly();
            this.anomalies.unshift(testAnomaly);
            
            // Обновляем UI
            this.updateAnomalyMarkers();
            this.updateAnomalyList();
            this.updateStatistics();
            
            this.showNotification('Обнаружена новая аномалия!', 'success');
            
            // Показываем на карте
            this.zoomToAnomaly(testAnomaly.id);
            
        } catch (error) {
            console.error('Ошибка тестового анализа:', error);
            this.showNotification('Ошибка при выполнении анализа', 'error');
        } finally {
            document.querySelector('.btn-success').innerHTML = originalText;
            document.querySelector('.btn-success').disabled = false;
        }
    }

    // Генерация тестовой аномалии
    generateTestAnomaly() {
        const types = ['fire', 'deforestation', 'dump', 'construction', 'flood'];
        const type = types[Math.floor(Math.random() * types.length)];
        const confidence = Math.floor(Math.random() * 30) + 70; // 70-100%
        
        // Генерация случайных координат рядом с центром карты
        const lat = AppConfig.MAP_CENTER[0] + (Math.random() - 0.5) * 5;
        const lng = AppConfig.MAP_CENTER[1] + (Math.random() - 0.5) * 10;
        
        return {
            id: `test_${Date.now()}`,
            type: type,
            title: `Тестовая ${this.getAnomalyTypeName(type).toLowerCase()}`,
            confidence: confidence / 100,
            latitude: lat,
            longitude: lng,
            detected_at: new Date().toISOString(),
            description: 'Аномалия обнаружена в ходе тестового анализа системы.',
            severity: confidence > 85 ? 'high' : 'medium',
            region: 'russia',
            area: `${Math.floor(Math.random() * 20) + 5} га`
        };
    }

    // Переход к аномалии на карте
    zoomToAnomaly(anomalyId) {
        const anomaly = this.anomalies.find(a => a.id === anomalyId);
        if (!anomaly) return;
        
        this.map.setView([anomaly.latitude, anomaly.longitude], 12);
        
        // Открываем попап маркера
        const marker = this.anomalyMarkers.get(anomalyId);
        if (marker) {
            marker.openPopup();
        }
        
        // Выделяем карточку
        this.highlightAnomalyCard(anomalyId);
    }

    // Выделение карточки аномалии
    highlightAnomalyCard(anomalyId) {
        // Снимаем выделение со всех карточек
        document.querySelectorAll('.anomaly-card').forEach(card => {
            card.classList.remove('active');
        });
        
        // Находим и выделяем нужную карточку
        const cards = document.querySelectorAll('.anomaly-card');
        const targetCard = Array.from(cards).find(card => 
            card.getAttribute('onclick')?.includes(anomalyId)
        );
        
        if (targetCard) {
            targetCard.classList.add('active');
            targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    // Экспорт данных
    async exportData() {
        this.showNotification('Подготовка данных для экспорта...', 'info');
        
        try {
            const filteredAnomalies = this.filterAnomaliesByType(this.anomalies);
            
            // Формируем CSV
            const headers = ['Тип', 'Уверенность%', 'Широта', 'Долгота', 'Дата', 'Описание', 'Серьезность'];
            const rows = filteredAnomalies.map(a => [
                this.getAnomalyTypeName(a.type),
                Math.round(a.confidence * 100),
                a.latitude.toFixed(6),
                a.longitude.toFixed(6),
                new Date(a.detected_at).toLocaleDateString('ru-RU'),
                a.description,
                this.getSeverityName(a.severity)
            ]);
            
            const csvContent = [
                headers.join(','),
                ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
            ].join('\n');
            
            // Создаем и скачиваем файл
            const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `anomalies_${new Date().toISOString().slice(0, 10)}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showNotification('Данные успешно экспортированы', 'success');
            
        } catch (error) {
            console.error('Ошибка экспорта:', error);
            this.showNotification('Ошибка при экспорте данных', 'error');
        }
    }

    // Показ деталей аномалии
    showAnomalyDetail(anomalyId) {
        const anomaly = this.anomalies.find(a => a.id === anomalyId);
        if (!anomaly) return;
        
        const modal = document.getElementById('detailModal');
        const content = document.getElementById('detailContent');
        
        if (!modal || !content) {
            console.error('Модальное окно не найдено');
            return;
        }
        
        // Заполняем контент
        content.innerHTML = this.createDetailContent(anomaly);
        
        // Показываем модальное окно
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Инициализируем мини-карту
        this.initDetailMap(anomaly);
    }

    // Создание контента для детального просмотра
createDetailContent(anomaly) {
    const confidencePercent = Math.round(anomaly.confidence * 100);
    const date = new Date(anomaly.detected_at).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    return `
        <div class="detail-header">
            <div class="detail-title">
                <h3>${anomaly.title}</h3>
                <div class="detail-meta">
                    <span class="anomaly-type-badge ${anomaly.type}">
                        ${this.getAnomalyTypeName(anomaly.type)}
                    </span>
                    <span class="severity-badge severity-${anomaly.severity}">
                        ${this.getSeverityName(anomaly.severity)} риск
                    </span>
                </div>
            </div>
            <div class="detail-confidence">
                <div class="confidence-circle" style="background: ${this.getConfidenceColor(confidencePercent)}">
                    <span>${confidencePercent}%</span>
                </div>
                <div class="confidence-label">Уверенность</div>
            </div>
        </div>
        
        <div class="detail-grid">
            <div class="detail-section">
                <h4><i class="fas fa-info-circle"></i> Основная информация</h4>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Координаты</div>
                        <div class="info-value">${anomaly.latitude.toFixed(4)}, ${anomaly.longitude.toFixed(4)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Дата обнаружения</div>
                        <div class="info-value">${date}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Регион</div>
                        <div class="info-value">${this.getRegionName(anomaly.region)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Площадь</div>
                        <div class="info-value">${anomaly.area || 'Не указана'}</div>
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-map-marked-alt"></i> Расположение</h4>
                <div id="detailMap" style="height: 200px; width: 100%; border-radius: 8px;"></div>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-file-alt"></i> Описание</h4>
                <div class="description-content">
                    ${anomaly.description}
                </div>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-chart-line"></i> Рекомендации</h4>
                <div class="recommendations">
                    ${this.getRecommendations(anomaly)}
                </div>
            </div>
        </div>
        
        <div class="detail-actions">
            <button class="btn-secondary" onclick="app.zoomToAnomaly('${anomaly.id}')">
                <i class="fas fa-search-location"></i> Показать на карте
            </button>
            <button class="btn-primary" onclick="app.generateReport('${anomaly.id}')">
                <i class="fas fa-file-download"></i> Создать отчет
            </button>
        </div>
    `;
}}


