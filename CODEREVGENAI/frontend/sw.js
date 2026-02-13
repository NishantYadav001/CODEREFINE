const CACHE_NAME = 'coderefine-v1';
const ASSETS = [
    './index.html',
    'https://cdn.tailwindcss.com',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js'
];

self.addEventListener('install', (e) => {
    e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
    e.respondWith(
        caches.match(e.request).then((response) => {
            return response || fetch(e.request).then((fetchRes) => {
                return caches.open(CACHE_NAME).then((cache) => {
                    if(e.request.method === 'GET' && e.request.url.startsWith('http')) cache.put(e.request, fetchRes.clone());
                    return fetchRes;
                });
            });
        })
    );
});