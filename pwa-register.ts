// Register Service Worker and enable PWA features

export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('✅ Service Worker registered:', registration);

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New service worker available
                showUpdateNotification();
              }
            });
          }
        });

        // Enable push notifications
        if ('PushManager' in window) {
          await requestNotificationPermission();
        }

        // Enable background sync
        if ('sync' in registration) {
          console.log('✅ Background sync available');
        }

      } catch (error) {
        console.error('❌ Service Worker registration failed:', error);
      }
    });
  }
}

async function requestNotificationPermission() {
  if (Notification.permission === 'default') {
    const permission = await Notification.requestPermission();
    console.log('Notification permission:', permission);
  }
}

function showUpdateNotification() {
  if (Notification.permission === 'granted') {
    new Notification('NetScan Update Available', {
      body: 'A new version is available. Refresh to update.',
      icon: '/icon-192.png',
      badge: '/icon-96.png',
      vibrate: [200, 100, 200]
    });
  }
}

// Check if app is installed as PWA
export function isPWA(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches ||
         (window.navigator as any).standalone === true;
}

// Prompt user to install PWA
export function showInstallPrompt() {
  let deferredPrompt: any = null;

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button
    const installButton = document.getElementById('install-button');
    if (installButton) {
      installButton.style.display = 'block';
      installButton.addEventListener('click', async () => {
        if (deferredPrompt) {
          deferredPrompt.prompt();
          const { outcome } = await deferredPrompt.userChoice;
          console.log('Install prompt outcome:', outcome);
          deferredPrompt = null;
          installButton.style.display = 'none';
        }
      });
    }
  });

  window.addEventListener('appinstalled', () => {
    console.log('✅ PWA installed successfully');
    deferredPrompt = null;
  });
}

// Initialize PWA features
export function initPWA() {
  registerServiceWorker();
  showInstallPrompt();
  
  console.log('🚀 PWA initialized');
  console.log('📱 Is PWA:', isPWA());
}
