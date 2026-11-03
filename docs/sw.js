// Service worker: la app funciona sin internet y se actualiza sola.
const VERSION = 'v2-tutor';
const SHELL = ['./', './index.html', './app.js', './style.css', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png'];
const BANK = ["./bank/algoritmo.json", "./bank/analogia.json", "./bank/analogia_verbal.json", "./bank/codificacion.json", "./bank/condicional.json", "./bank/cubo.json", "./bank/domino.json", "./bank/espejo.json", "./bank/giro2d.json", "./bank/intrusa.json", "./bank/matriz.json", "./bank/numerico.json", "./bank/numeros_figura.json", "./bank/operador.json", "./bank/ordenamiento.json", "./bank/papel.json", "./bank/rotacion.json", "./bank/serie.json", "./bank/serie_letras.json", "./bank/serie_num.json", "./bank/silogismo.json", "./bank/simbolos.json", "./bank/superposicion.json", "./bank/tabla_logica.json", "./bank/verdad_mentira.json"];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL.concat(BANK))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  // primero la red (para recibir actualizaciones), si no hay internet, la copia guardada
  e.respondWith(fetch(req, { cache: 'no-cache' }).then(res => { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); return res; })
    .catch(() => caches.match(req).then(r => r || caches.match('./index.html'))));
});
