const CACHE='atelier-v14-rc-14.0.0-dev.19';
const RELEASE='14.0.0-dev.19';
const CORE=["./","./index.html","./manifest.webmanifest","./icon-192.png","./icon-512.png","./v14/shell/notifications.js","./v14/shell/dialogs.js","./v14/shell/commands.js","./v14/shell/files.js","./v14/shell/icons.js","./v14/shell/text.js","./v14/shell/units.js"];
async function verifyCore(){const cache=await caches.open(CACHE),missing=[];for(const path of CORE){if(!await cache.match(path))missing.push(path);}const keys=await caches.keys(),stale=keys.filter(k=>k.startsWith('atelier-v14-rc-')&&k!==CACHE);return {type:'ATELIER_SW_STATUS',version:RELEASE,cache:CACHE,core:CORE,ready:missing.length===0,missing,stale};}
async function clearStale(){const keys=await caches.keys(),stale=keys.filter(k=>k.startsWith('atelier-v14-rc-')&&k!==CACHE);await Promise.all(stale.map(k=>caches.delete(k)));return stale;}
self.addEventListener('install',event=>event.waitUntil((async()=>{try{const cache=await caches.open(CACHE);await cache.addAll(CORE);const status=await verifyCore();if(!status.ready)throw new Error('Offline shell verification failed: '+status.missing.join(', '));}catch(error){await caches.delete(CACHE);throw error;}})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{await clearStale();await self.clients.claim();})()));
self.addEventListener('message',event=>{
 const type=event.data?.type,reply=data=>{try{event.ports?.[0]?.postMessage(data);}catch{}};
 if(type==='ACTIVATE_UPDATE'){event.waitUntil(self.skipWaiting());return;}
 if(type==='GET_STATUS'){event.waitUntil(verifyCore().then(reply));return;}
 if(type==='PING'){reply({type:'ATELIER_SW_PONG',version:RELEASE,cache:CACHE});return;}
 if(type==='VERIFY_CORE'){event.waitUntil(verifyCore().then(reply));return;}
 if(type==='CLEAR_STALE_CACHES'){event.waitUntil(clearStale().then(deleted=>reply({type:'ATELIER_STALE_CACHES_CLEARED',deleted,cache:CACHE})));return;}
});
self.addEventListener('fetch',event=>{
 if(event.request.method!=='GET')return;
 event.respondWith((async()=>{
   const cache=await caches.open(CACHE);
   const cached=await cache.match(event.request);
   if(cached)return cached;
   try{
     const response=await fetch(event.request);
     if(response&&response.ok&&new URL(event.request.url).origin===self.location.origin){const cache=await caches.open(CACHE);await cache.put(event.request,response.clone());}
     return response;
   }catch{
     if(event.request.mode==='navigate')return (await cache.match('./index.html'))||(await cache.match('./'))||Response.error();
     return Response.error();
   }
 })());
});
