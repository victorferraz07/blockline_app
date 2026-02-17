// 📍 Geolocalização - Blockline PWA
// Sistema para validar localização ao bater ponto

class GeolocationManager {
    constructor() {
        this.currentPosition = null;
        this.watchId = null;
        this.allowedLocations = []; // Lista de localizações permitidas
    }

    // Verificar se geolocalização é suportada
    isSupported() {
        return 'geolocation' in navigator;
    }

    // Obter posição atual
    async getCurrentPosition(options = {}) {
        if (!this.isSupported()) {
            throw new Error('Geolocalização não é suportada neste dispositivo');
        }

        const defaultOptions = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        };

        const geoOptions = { ...defaultOptions, ...options };

        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.currentPosition = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: position.timestamp
                    };

                    console.log('📍 Localização obtida:', this.currentPosition);
                    resolve(this.currentPosition);
                },
                (error) => {
                    console.error('❌ Erro ao obter localização:', error);
                    this.handleGeolocationError(error);
                    reject(error);
                },
                geoOptions
            );
        });
    }

    // Monitorar posição continuamente
    watchPosition(onPositionUpdate, options = {}) {
        if (!this.isSupported()) {
            throw new Error('Geolocalização não é suportada neste dispositivo');
        }

        const defaultOptions = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 1000
        };

        const geoOptions = { ...defaultOptions, ...options };

        this.watchId = navigator.geolocation.watchPosition(
            (position) => {
                this.currentPosition = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: position.timestamp
                };

                if (onPositionUpdate) {
                    onPositionUpdate(this.currentPosition);
                }
            },
            (error) => {
                console.error('Erro ao monitorar localização:', error);
                this.handleGeolocationError(error);
            },
            geoOptions
        );

        console.log('👁️ Monitoramento de localização iniciado');
    }

    // Parar monitoramento
    stopWatching() {
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
            console.log('🛑 Monitoramento de localização parado');
        }
    }

    // Calcular distância entre dois pontos (fórmula de Haversine)
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371e3; // Raio da Terra em metros
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lon2 - lon1) * Math.PI / 180;

        const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
                  Math.cos(φ1) * Math.cos(φ2) *
                  Math.sin(Δλ / 2) * Math.sin(Δλ / 2);

        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        const distance = R * c; // Distância em metros

        return distance;
    }

    // Verificar se está dentro de um raio permitido
    isWithinRadius(targetLat, targetLon, maxRadius = 100) {
        if (!this.currentPosition) {
            throw new Error('Posição atual não disponível');
        }

        const distance = this.calculateDistance(
            this.currentPosition.latitude,
            this.currentPosition.longitude,
            targetLat,
            targetLon
        );

        return {
            withinRadius: distance <= maxRadius,
            distance: Math.round(distance),
            maxRadius: maxRadius
        };
    }

    // Configurar locais permitidos (ex: escritório da empresa)
    setAllowedLocations(locations) {
        // Formato: [{ name: 'Escritório', lat: -23.550520, lon: -46.633308, radius: 100 }]
        this.allowedLocations = locations;
        console.log('📍 Locais permitidos configurados:', locations);
    }

    // Verificar se está em local permitido
    async isInAllowedLocation() {
        if (this.allowedLocations.length === 0) {
            // Se não há locais configurados, permitir qualquer local
            return { allowed: true, reason: 'Nenhum local configurado' };
        }

        if (!this.currentPosition) {
            await this.getCurrentPosition();
        }

        for (const location of this.allowedLocations) {
            const check = this.isWithinRadius(
                location.lat,
                location.lon,
                location.radius || 100
            );

            if (check.withinRadius) {
                return {
                    allowed: true,
                    location: location.name,
                    distance: check.distance
                };
            }
        }

        // Não está em nenhum local permitido
        const nearest = this.findNearestLocation();
        return {
            allowed: false,
            reason: `Você está fora dos locais permitidos (${nearest.distance}m do ${nearest.name})`,
            nearest: nearest
        };
    }

    // Encontrar local permitido mais próximo
    findNearestLocation() {
        if (!this.currentPosition || this.allowedLocations.length === 0) {
            return null;
        }

        let nearest = null;
        let minDistance = Infinity;

        for (const location of this.allowedLocations) {
            const distance = this.calculateDistance(
                this.currentPosition.latitude,
                this.currentPosition.longitude,
                location.lat,
                location.lon
            );

            if (distance < minDistance) {
                minDistance = distance;
                nearest = {
                    name: location.name,
                    distance: Math.round(distance)
                };
            }
        }

        return nearest;
    }

    // Tratar erros de geolocalização
    handleGeolocationError(error) {
        switch (error.code) {
            case error.PERMISSION_DENIED:
                alert('⚠️ Permissão de localização negada. Por favor, permita o acesso nas configurações.');
                break;
            case error.POSITION_UNAVAILABLE:
                alert('⚠️ Informação de localização indisponível.');
                break;
            case error.TIMEOUT:
                alert('⚠️ Tempo esgotado ao obter localização. Tente novamente.');
                break;
            default:
                alert('⚠️ Erro desconhecido ao obter localização.');
                break;
        }
    }

    // Obter endereço a partir de coordenadas (requer API externa)
    async getAddressFromCoordinates(lat, lon) {
        try {
            // Usando Nominatim (OpenStreetMap) - gratuito mas com rate limit
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`,
                {
                    headers: {
                        'User-Agent': 'Blockline-PWA'
                    }
                }
            );

            const data = await response.json();

            return {
                street: data.address.road || '',
                number: data.address.house_number || '',
                neighborhood: data.address.suburb || data.address.neighbourhood || '',
                city: data.address.city || data.address.town || '',
                state: data.address.state || '',
                country: data.address.country || '',
                formatted: data.display_name
            };
        } catch (error) {
            console.error('Erro ao obter endereço:', error);
            return null;
        }
    }

    // Abrir localização no Google Maps
    openInMaps(lat = null, lon = null) {
        const latitude = lat || this.currentPosition?.latitude;
        const longitude = lon || this.currentPosition?.longitude;

        if (!latitude || !longitude) {
            alert('⚠️ Localização não disponível');
            return;
        }

        const url = `https://www.google.com/maps?q=${latitude},${longitude}`;
        window.open(url, '_blank');
    }

    // Formatar coordenadas para exibição
    formatCoordinates(lat = null, lon = null) {
        const latitude = lat || this.currentPosition?.latitude;
        const longitude = lon || this.currentPosition?.longitude;

        if (!latitude || !longitude) {
            return 'Localização não disponível';
        }

        return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
    }
}

// Integração com sistema de ponto
class PontoGeolocation {
    constructor() {
        this.geo = new GeolocationManager();
        this.validationEnabled = true;
    }

    // Configurar locais da empresa
    setupCompanyLocations() {
        // EXEMPLO: Configure aqui os locais da sua empresa
        this.geo.setAllowedLocations([
            {
                name: 'Escritório Principal',
                lat: -23.550520,  // Substitua pela latitude real
                lon: -46.633308,  // Substitua pela longitude real
                radius: 100       // Raio de 100 metros
            },
            // Adicione mais locais se necessário
            // {
            //     name: 'Filial',
            //     lat: -23.xxx,
            //     lon: -46.xxx,
            //     radius: 50
            // }
        ]);
    }

    // Validar localização antes de bater ponto
    async validateLocation() {
        if (!this.validationEnabled) {
            return { valid: true, message: 'Validação de localização desabilitada' };
        }

        try {
            // Obter localização atual
            await this.geo.getCurrentPosition();

            // Verificar se está em local permitido
            const check = await this.geo.isInAllowedLocation();

            if (check.allowed) {
                return {
                    valid: true,
                    message: `✅ Localização válida (${check.location || 'permitido'})`,
                    location: this.geo.currentPosition
                };
            } else {
                return {
                    valid: false,
                    message: `❌ ${check.reason}`,
                    location: this.geo.currentPosition,
                    nearest: check.nearest
                };
            }
        } catch (error) {
            return {
                valid: false,
                message: '❌ Não foi possível validar localização',
                error: error.message
            };
        }
    }

    // Adicionar localização ao formulário de ponto
    async addLocationToForm(formElement) {
        try {
            const position = await this.geo.getCurrentPosition();

            // Criar campos ocultos no formulário
            let latInput = formElement.querySelector('input[name="latitude"]');
            let lonInput = formElement.querySelector('input[name="longitude"]');

            if (!latInput) {
                latInput = document.createElement('input');
                latInput.type = 'hidden';
                latInput.name = 'latitude';
                formElement.appendChild(latInput);
            }

            if (!lonInput) {
                lonInput = document.createElement('input');
                lonInput.type = 'hidden';
                lonInput.name = 'longitude';
                formElement.appendChild(lonInput);
            }

            latInput.value = position.latitude;
            lonInput.value = position.longitude;

            console.log('📍 Localização adicionada ao formulário:', position);
            return true;
        } catch (error) {
            console.error('Erro ao adicionar localização:', error);
            return false;
        }
    }
}

// Instância global
window.geolocationManager = new GeolocationManager();
window.pontoGeolocation = new PontoGeolocation();

// Configurar locais da empresa (chame isso no carregamento da página)
document.addEventListener('DOMContentLoaded', () => {
    window.pontoGeolocation.setupCompanyLocations();
});

// Funções globais de fácil acesso
window.getCurrentLocation = async () => {
    return await window.geolocationManager.getCurrentPosition();
};

window.validatePontoLocation = async () => {
    return await window.pontoGeolocation.validateLocation();
};

window.getLocationInfo = () => {
    const pos = window.geolocationManager.currentPosition;
    if (!pos) return 'Localização não obtida';

    return {
        coordinates: window.geolocationManager.formatCoordinates(),
        accuracy: `${Math.round(pos.accuracy)}m`,
        timestamp: new Date(pos.timestamp).toLocaleString()
    };
};

console.log('📍 Sistema de geolocalização carregado');
