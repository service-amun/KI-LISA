// © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
// Service Worker — AILIZA PWA
// Cacht nur statische Assets; API-Anfragen immer live (Compliance-Pflicht).

const CACHE = 'ailiza-v1';
const STATIC = ['/dashboard', '/setup'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(STATIC)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  // API-Calls niemals cachen (DSGVO: kein Client-Side-Caching von Nutzerdaten)
  if (e.request.url.includes('/sessions') ||
      e.request.url.includes('/ai/') ||
      e.request.url.includes('/upload') ||
      e.request.url.includes('/audit')) {
    return;
  }
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
