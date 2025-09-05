// Service Worker for LocalBriefing
const CACHE_NAME = 'localbriefing-v1';

self.addEventListener('install', function(event) {
  console.log('Service Worker installing');
});

self.addEventListener('activate', function(event) {
  console.log('Service Worker activating');
});

self.addEventListener('fetch', function(event) {
  // Basic fetch handling
});