// Blockline PWA Service Worker
const CACHE_NAME = 'blockline-v1.0.0';
const OFFLINE_URL = '/offline/';

// Arquivos essenciais para cache
const ESSENTIAL_CACHE = [
  '/',
  '/static/manifest.json',
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js',
];

// Páginas principais para cache
const PAGE_CACHE = [
  '/',
  '/estoque/',
  '/kanban/',
  '/ponto/',
  '/recebimento/',
  '/expedicao/',
  '/produtos/',
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Instalando Service Worker...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Cache aberto');
        return cache.addAll(ESSENTIAL_CACHE);
      })
      .then(() => self.skipWaiting()) // Ativa imediatamente
  );
});

// Ativação e limpeza de caches antigos
self.addEventListener('activate', (event) => {
  console.log('[SW] Ativando Service Worker...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim()) // Controla imediatamente
  );
});

// Estratégia de fetch: Network First, falling back to Cache
self.addEventListener('fetch', (event) => {
  // Ignorar requisições que não são GET
  if (event.request.method !== 'GET') return;

  // Ignorar requisições externas (exceto CDNs essenciais)
  const url = new URL(event.request.url);
  if (url.origin !== location.origin &&
      !url.hostname.includes('cdn.tailwindcss.com') &&
      !url.hostname.includes('cdn.jsdelivr.net')) {
    return;
  }

  event.respondWith(
    // Tenta buscar da rede primeiro
    fetch(event.request)
      .then((response) => {
        // Clona a resposta (pode ser usada apenas uma vez)
        const responseToCache = response.clone();

        // Armazena no cache para uso offline
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return response;
      })
      .catch(() => {
        // Se falhar, busca do cache
        return caches.match(event.request)
          .then((response) => {
            if (response) {
              console.log('[SW] Servindo do cache:', event.request.url);
              return response;
            }

            // Se não encontrar no cache, retorna página offline (se disponível)
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL);
            }
          });
      })
  );
});

// Sincronização em background (quando voltar online)
self.addEventListener('sync', (event) => {
  console.log('[SW] Sincronizando dados...');

  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  // Implementar sincronização de dados offline aqui
  console.log('[SW] Sincronizando dados pendentes...');

  try {
    // Buscar dados do IndexedDB
    // Enviar para o servidor
    // Limpar dados locais após sucesso

    return Promise.resolve();
  } catch (error) {
    console.error('[SW] Erro na sincronização:', error);
    return Promise.reject(error);
  }
}

// Notificações Push (futuro)
self.addEventListener('push', (event) => {
  console.log('[SW] Push recebido');

  const options = {
    body: event.data ? event.data.text() : 'Nova notificação do Blockline',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/badge-72.png',
    vibrate: [200, 100, 200],
    tag: 'blockline-notification',
    requireInteraction: false,
  };

  event.waitUntil(
    self.registration.showNotification('Blockline', options)
  );
});

// Clique em notificação
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notificação clicada');

  event.notification.close();

  event.waitUntil(
    clients.openWindow('/')
  );
});

console.log('[SW] Service Worker carregado!');
