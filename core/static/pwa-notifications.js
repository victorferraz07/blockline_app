// 🔔 Sistema de Notificações Push - Blockline PWA

class NotificationManager {
    constructor() {
        this.permission = Notification.permission;
        this.registration = null;
    }

    // Verificar se notificações são suportadas
    isSupported() {
        return 'Notification' in window && 'serviceWorker' in navigator;
    }

    // Solicitar permissão para notificações
    async requestPermission() {
        if (!this.isSupported()) {
            console.warn('❌ Notificações não são suportadas neste navegador');
            return false;
        }

        try {
            const permission = await Notification.requestPermission();
            this.permission = permission;

            if (permission === 'granted') {
                console.log('✅ Permissão de notificações concedida');
                return true;
            } else if (permission === 'denied') {
                console.warn('❌ Permissão de notificações negada');
                return false;
            } else {
                console.warn('⚠️ Permissão de notificações não definida');
                return false;
            }
        } catch (error) {
            console.error('Erro ao solicitar permissão:', error);
            return false;
        }
    }

    // Enviar notificação local
    async sendNotification(title, options = {}) {
        if (this.permission !== 'granted') {
            console.warn('⚠️ Permissão necessária para enviar notificações');
            return;
        }

        const defaultOptions = {
            icon: '/static/icons/icon-192.png',
            badge: '/static/icons/icon-192.png',
            vibrate: [200, 100, 200],
            tag: 'blockline-notification',
            requireInteraction: false,
        };

        const notificationOptions = { ...defaultOptions, ...options };

        try {
            // Se temos service worker registrado, usa ele
            if (this.registration) {
                await this.registration.showNotification(title, notificationOptions);
            } else {
                // Fallback para notificação local
                new Notification(title, notificationOptions);
            }

            console.log('📬 Notificação enviada:', title);
        } catch (error) {
            console.error('Erro ao enviar notificação:', error);
        }
    }

    // Configurar service worker para notificações
    async setupServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            return;
        }

        try {
            this.registration = await navigator.serviceWorker.ready;
            console.log('✅ Service Worker pronto para notificações');
        } catch (error) {
            console.error('Erro ao configurar Service Worker:', error);
        }
    }

    // Notificações específicas do Blockline

    // Lembrete de bater ponto
    notifyPonto(tipo) {
        const messages = {
            entrada: {
                title: '🟢 Bom dia!',
                body: 'Não esqueça de registrar sua entrada',
            },
            saida: {
                title: '🔴 Hora de ir!',
                body: 'Não esqueça de registrar sua saída',
            },
            almoco: {
                title: '🍽️ Hora do almoço',
                body: 'Bom apetite! Registre seu horário',
            }
        };

        const msg = messages[tipo] || messages.entrada;

        this.sendNotification(msg.title, {
            body: msg.body,
            icon: '/static/icons/icon-192.png',
            tag: 'ponto-reminder',
            requireInteraction: true,
            actions: [
                { action: 'open', title: 'Abrir Ponto' },
                { action: 'dismiss', title: 'Fechar' }
            ]
        });
    }

    // Alerta de estoque baixo
    notifyEstoqueBaixo(produto, quantidade) {
        this.sendNotification('⚠️ Estoque Baixo', {
            body: `${produto}: apenas ${quantidade} unidades restantes`,
            icon: '/static/icons/icon-192.png',
            tag: 'estoque-baixo',
            requireInteraction: true,
            vibrate: [300, 200, 300],
        });
    }

    // Nova tarefa no Kanban
    notifyNovaTarefa(tarefa) {
        this.sendNotification('📌 Nova Tarefa', {
            body: `Nova tarefa atribuída: ${tarefa}`,
            icon: '/static/icons/icon-192.png',
            tag: 'nova-tarefa',
        });
    }

    // Expedição pendente
    notifyExpedicao(cliente) {
        this.sendNotification('🚚 Expedição Pendente', {
            body: `Expedição para ${cliente} aguardando processamento`,
            icon: '/static/icons/icon-192.png',
            tag: 'expedicao-pendente',
        });
    }

    // Agendar notificação de lembrete de ponto
    schedulePointoReminders() {
        // Entrada: 7:55 (5min antes das 8h)
        this.scheduleNotificationAt(7, 55, () => {
            this.notifyPonto('entrada');
        });

        // Almoço: 11:55
        this.scheduleNotificationAt(11, 55, () => {
            this.notifyPonto('almoco');
        });

        // Saída: 17:55 (sexta) ou 17:55 (segunda a quinta)
        const diaSemana = new Date().getDay();
        if (diaSemana === 5) { // Sexta
            this.scheduleNotificationAt(16, 55, () => {
                this.notifyPonto('saida');
            });
        } else if (diaSemana >= 1 && diaSemana <= 4) { // Seg-Qui
            this.scheduleNotificationAt(17, 55, () => {
                this.notifyPonto('saida');
            });
        }
    }

    // Agendar notificação para horário específico
    scheduleNotificationAt(hour, minute, callback) {
        const now = new Date();
        const scheduled = new Date();
        scheduled.setHours(hour, minute, 0, 0);

        // Se o horário já passou hoje, agendar para amanhã
        if (scheduled <= now) {
            scheduled.setDate(scheduled.getDate() + 1);
        }

        const timeUntil = scheduled - now;

        setTimeout(() => {
            callback();
            // Reagendar para o próximo dia
            this.scheduleNotificationAt(hour, minute, callback);
        }, timeUntil);

        console.log(`⏰ Notificação agendada para ${scheduled.toLocaleString()}`);
    }
}

// Instância global
window.notificationManager = new NotificationManager();

// Inicializar quando o DOM carregar
document.addEventListener('DOMContentLoaded', async () => {
    if (window.notificationManager.isSupported()) {
        await window.notificationManager.setupServiceWorker();

        // Se já tem permissão, configurar lembretes
        if (Notification.permission === 'granted') {
            window.notificationManager.schedulePointoReminders();
        }
    }
});

// Exportar para uso global
window.requestNotificationPermission = async () => {
    const granted = await window.notificationManager.requestPermission();
    if (granted) {
        window.notificationManager.schedulePointoReminders();
    }
    return granted;
};

window.sendNotification = (title, options) => {
    window.notificationManager.sendNotification(title, options);
};

console.log('🔔 Sistema de notificações carregado');
