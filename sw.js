// Mémoire de l'appli : on affiche tout de suite la version gardée, et on la rafraîchit en arrière-plan
const CACHE = "ou-sortir-v3";
const FICHIERS = ["./", "index.html", "manifest.json", "icone-192.png", "icone-512.png", "data/lieux-lille.json"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FICHIERS).catch(() => {}))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== CACHE).map(x => caches.delete(x))))); self.clients.claim(); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;   // OpenStreetMap, Google… : pas touché
  e.respondWith(caches.open(CACHE).then(async c => {
    const garde = await c.match(e.request, { ignoreSearch: true });
    const frais = fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }).catch(() => garde);
    return garde || frais;
  }));
});
