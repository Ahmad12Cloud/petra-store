/* Petra Electric service worker: app shell works offline, always fetches the newest code when online */
const V='pp88-shop-1',IMG='pp88-img';
const SHELL=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>Promise.all(SHELL.map(u=>c.add(u).catch(()=>{})))).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('pp55-')||k.startsWith('pp56-')||k.startsWith('pp57-')||k.startsWith('pp58-')||k.startsWith('pp59-')||k.startsWith('pp60-')||k.startsWith('pp61-')||k.startsWith('pp62-')||k.startsWith('pp63-')||k.startsWith('pp64-')||k.startsWith('pp57-shop-')&&k!==V||k.startsWith('pp53-')).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const u=new URL(r.url);
  if(u.origin===location.origin){
    e.respondWith(fetch(r).then(res=>{if(res.ok){const c=res.clone();caches.open(V).then(ca=>ca.put(r,c));}return res;}).catch(()=>caches.match(r).then(m=>m||caches.match('index.html'))));
  }else if(u.hostname.endsWith('.supabase.co')&&u.pathname.startsWith('/storage/v1/object/public/')){
    e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{if(res.ok){const c=res.clone();caches.open(IMG).then(ca=>ca.put(r,c));}return res;})));
  }
});
