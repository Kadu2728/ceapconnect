// Service worker do CEAP Connect (EPIC 18 — PWA + push notifications).
//
// Duas responsabilidades, deliberadamente mínimas:
// 1. Um handler de `fetch` (mesmo que passthrough) — exigido pelos
//    navegadores para considerar o app instalável.
// 2. Push notifications reais: recebe o payload enviado pelo backend
//    (título/corpo/url) e mostra a notificação do sistema operacional,
//    mesmo com o app fechado.

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", () => {
  // Passthrough — sem cache customizado por enquanto. Existir já habilita a
  // instalabilidade do PWA; estratégias de cache offline podem vir depois.
});

self.addEventListener("push", (event) => {
  if (!event.data) return;

  let payload;
  try {
    payload = event.data.json();
  } catch {
    payload = { title: "CEAP Connect", body: event.data.text() };
  }

  const title = payload.title || "CEAP Connect";
  const options = {
    body: payload.body || "",
    icon: "/icons/icon192.png",
    badge: "/icons/icon192.png",
    data: { url: payload.url || "/dashboard" },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl = event.notification.data?.url || "/dashboard";

  event.waitUntil(
    self.clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((clients) => {
        for (const client of clients) {
          if (client.url.includes(targetUrl) && "focus" in client) {
            return client.focus();
          }
        }
        if (self.clients.openWindow) {
          return self.clients.openWindow(targetUrl);
        }
        return undefined;
      }),
  );
});
