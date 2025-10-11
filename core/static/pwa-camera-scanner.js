// 📸 Scanner de Câmera - Blockline PWA
// Suporte para QR Code e Código de Barras

class CameraScanner {
    constructor() {
        this.stream = null;
        this.videoElement = null;
        this.canvasElement = null;
        this.isScanning = false;
        this.onScanCallback = null;
    }

    // Verificar se câmera é suportada
    isSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }

    // Inicializar scanner
    async initialize(videoElementId, canvasElementId = null) {
        if (!this.isSupported()) {
            throw new Error('Câmera não é suportada neste dispositivo');
        }

        this.videoElement = document.getElementById(videoElementId);
        if (canvasElementId) {
            this.canvasElement = document.getElementById(canvasElementId);
        }

        if (!this.videoElement) {
            throw new Error('Elemento de vídeo não encontrado');
        }
    }

    // Solicitar permissão e iniciar câmera
    async startCamera(facingMode = 'environment') {
        try {
            // Configurações da câmera
            const constraints = {
                video: {
                    facingMode: facingMode, // 'user' (frontal) ou 'environment' (traseira)
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                },
                audio: false
            };

            // Solicitar acesso à câmera
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);

            // Atribuir stream ao elemento de vídeo
            this.videoElement.srcObject = this.stream;
            this.videoElement.setAttribute('playsinline', true);
            await this.videoElement.play();

            console.log('✅ Câmera iniciada com sucesso');
            return true;
        } catch (error) {
            console.error('❌ Erro ao acessar câmera:', error);
            this.handleCameraError(error);
            return false;
        }
    }

    // Parar câmera
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
            if (this.videoElement) {
                this.videoElement.srcObject = null;
            }
            console.log('🛑 Câmera parada');
        }
        this.isScanning = false;
    }

    // Capturar foto
    capturePhoto() {
        if (!this.videoElement || !this.canvasElement) {
            throw new Error('Elementos de vídeo/canvas não configurados');
        }

        const context = this.canvasElement.getContext('2d');
        this.canvasElement.width = this.videoElement.videoWidth;
        this.canvasElement.height = this.videoElement.videoHeight;

        context.drawImage(
            this.videoElement,
            0, 0,
            this.canvasElement.width,
            this.canvasElement.height
        );

        // Retornar como Data URL
        return this.canvasElement.toDataURL('image/jpeg', 0.8);
    }

    // Iniciar escaneamento contínuo (para integração com biblioteca de QR/Barcode)
    startScanning(onScanCallback, interval = 100) {
        if (!this.stream) {
            throw new Error('Câmera não está ativa');
        }

        this.isScanning = true;
        this.onScanCallback = onScanCallback;

        // Loop de escaneamento
        this.scanLoop(interval);

        console.log('🔍 Escaneamento iniciado');
    }

    // Loop de escaneamento
    scanLoop(interval) {
        if (!this.isScanning) return;

        // Tentar ler código da imagem
        this.detectCode();

        // Continuar loop
        setTimeout(() => this.scanLoop(interval), interval);
    }

    // Detectar código (requer biblioteca externa como ZXing ou html5-qrcode)
    detectCode() {
        // Este é um placeholder - você deve integrar uma biblioteca como:
        // - html5-qrcode: https://github.com/mebjas/html5-qrcode
        // - ZXing: https://github.com/zxing-js/library
        // - quagga: https://github.com/serratus/quaggaJS

        // Exemplo de integração estará no componente UI
        console.log('🔎 Tentando detectar código...');
    }

    // Parar escaneamento
    stopScanning() {
        this.isScanning = false;
        console.log('🛑 Escaneamento parado');
    }

    // Alternar entre câmera frontal e traseira
    async switchCamera() {
        const currentFacingMode = this.stream?.getVideoTracks()[0]?.getSettings()?.facingMode;
        const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';

        this.stopCamera();
        await this.startCamera(newFacingMode);
    }

    // Tratar erros da câmera
    handleCameraError(error) {
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            alert('⚠️ Permissão de câmera negada. Por favor, permita o acesso nas configurações do navegador.');
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            alert('⚠️ Nenhuma câmera encontrada neste dispositivo.');
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            alert('⚠️ Câmera está sendo usada por outro aplicativo.');
        } else {
            alert(`⚠️ Erro ao acessar câmera: ${error.message}`);
        }
    }

    // Listar câmeras disponíveis
    async listCameras() {
        if (!this.isSupported()) {
            return [];
        }

        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const cameras = devices.filter(device => device.kind === 'videoinput');
            console.log('📹 Câmeras disponíveis:', cameras);
            return cameras;
        } catch (error) {
            console.error('Erro ao listar câmeras:', error);
            return [];
        }
    }
}

// UI Component para Scanner
class ScannerUI {
    constructor() {
        this.scanner = new CameraScanner();
        this.modalElement = null;
    }

    // Criar modal de scanner
    createScannerModal() {
        const modalHTML = `
            <div id="scanner-modal" class="fixed inset-0 bg-black bg-opacity-90 z-50 hidden">
                <div class="relative w-full h-full flex flex-col">
                    <!-- Header -->
                    <div class="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/80 to-transparent p-4 z-10">
                        <div class="flex items-center justify-between">
                            <h3 class="text-white font-bold text-lg">📸 Scanner</h3>
                            <button onclick="window.closeScannerModal()" class="text-white hover:text-gray-300 p-2">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Vídeo -->
                    <div class="flex-1 relative overflow-hidden">
                        <video id="scanner-video" class="w-full h-full object-cover" playsinline></video>

                        <!-- Overlay de scanning -->
                        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div class="w-64 h-64 border-4 border-white rounded-lg shadow-lg">
                                <div class="w-full h-full bg-white/10"></div>
                            </div>
                        </div>

                        <!-- Instrução -->
                        <div class="absolute bottom-24 left-0 right-0 text-center">
                            <p class="text-white font-semibold bg-black/50 px-4 py-2 rounded-full inline-block">
                                Posicione o código dentro do quadrado
                            </p>
                        </div>
                    </div>

                    <!-- Footer com controles -->
                    <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                        <div class="flex items-center justify-around">
                            <!-- Botão capturar foto -->
                            <button onclick="window.captureFromScanner()" class="bg-white hover:bg-gray-200 text-black font-bold p-4 rounded-full">
                                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                                </svg>
                            </button>

                            <!-- Botão alternar câmera -->
                            <button onclick="window.switchScannerCamera()" class="bg-white/20 hover:bg-white/30 text-white font-bold p-4 rounded-full">
                                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Canvas oculto para captura -->
                    <canvas id="scanner-canvas" class="hidden"></canvas>
                </div>
            </div>
        `;

        // Adicionar ao body se não existir
        if (!document.getElementById('scanner-modal')) {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        this.modalElement = document.getElementById('scanner-modal');
    }

    // Abrir scanner
    async openScanner(onScanCallback) {
        if (!this.scanner.isSupported()) {
            alert('⚠️ Câmera não é suportada neste dispositivo');
            return;
        }

        this.createScannerModal();

        // Inicializar scanner
        await this.scanner.initialize('scanner-video', 'scanner-canvas');

        // Mostrar modal
        this.modalElement.classList.remove('hidden');

        // Iniciar câmera
        const started = await this.scanner.startCamera('environment');

        if (started && onScanCallback) {
            this.scanner.startScanning(onScanCallback);
        }
    }

    // Fechar scanner
    closeScanner() {
        if (this.scanner) {
            this.scanner.stopScanning();
            this.scanner.stopCamera();
        }

        if (this.modalElement) {
            this.modalElement.classList.add('hidden');
        }
    }

    // Capturar foto manual
    capturePhoto() {
        try {
            const photoDataUrl = this.scanner.capturePhoto();
            console.log('📸 Foto capturada');

            // Vibrar se disponível
            if (navigator.vibrate) {
                navigator.vibrate(100);
            }

            return photoDataUrl;
        } catch (error) {
            console.error('Erro ao capturar foto:', error);
            alert('⚠️ Erro ao capturar foto');
            return null;
        }
    }

    // Alternar câmera
    async switchCamera() {
        await this.scanner.switchCamera();
    }
}

// Instância global
window.scannerUI = new ScannerUI();

// Funções globais para fácil acesso
window.openScanner = (onScanCallback) => {
    return window.scannerUI.openScanner(onScanCallback);
};

window.closeScannerModal = () => {
    window.scannerUI.closeScanner();
};

window.captureFromScanner = () => {
    const photo = window.scannerUI.capturePhoto();
    if (photo) {
        // Aqui você pode fazer algo com a foto capturada
        console.log('Foto disponível:', photo.substring(0, 50) + '...');
        // Por exemplo, enviar para um campo de formulário ou fazer upload
    }
    return photo;
};

window.switchScannerCamera = () => {
    window.scannerUI.switchCamera();
};

console.log('📸 Sistema de câmera carregado');
