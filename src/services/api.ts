/**
 * NetScan API Service
 * Connects the React frontend to the FastAPI backend.
 *
 * In development the Vite proxy forwards /api/* to localhost:8000.
 * In production VITE_API_URL must be set to the Railway backend URL.
 */

import axios from 'axios';

// Use the env var if present, otherwise rely on the Vite dev proxy ('')
const BASE_URL = (import.meta.env.VITE_API_URL as string) || '';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
});

// Attach JWT token to every request if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('netscan_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally — clear token and redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('netscan_token');
      // Reload to trigger auth flow
      window.location.reload();
    }
    return Promise.reject(err);
  },
);

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
export const authApi = {
  register: (email: string, password: string, fullName: string) =>
    api.post('/api/auth/register', { email, password, full_name: fullName }),

  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    return api.post('/api/auth/token', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
};

// ---------------------------------------------------------------------------
// Networks
// ---------------------------------------------------------------------------
export const networksApi = {
  list: () => api.get('/api/networks'),
  create: (name: string, subnet: string, iface: string, gateway?: string) =>
    api.post('/api/networks', { name, subnet, interface: iface, gateway }),
  delete: (id: string) => api.delete(`/api/networks/${id}`),
};

// ---------------------------------------------------------------------------
// Devices
// ---------------------------------------------------------------------------
export const devicesApi = {
  list: (networkId?: string) =>
    api.get('/api/devices', { params: networkId ? { network_id: networkId } : {} }),
  get: (id: string) => api.get(`/api/devices/${id}`),
  block: (id: string) => api.post(`/api/devices/${id}/block`),
  unblock: (id: string) => api.post(`/api/devices/${id}/unblock`),
};

// ---------------------------------------------------------------------------
// Scans
// ---------------------------------------------------------------------------
export const scanApi = {
  startNetworkScan: (networkId: string) => api.post(`/api/scan/network/${networkId}`),
  getInterfaces: () => api.get('/api/scan/interfaces'),
  getHistory: (networkId: string) => api.get(`/api/scan/history/${networkId}`),
};

// ---------------------------------------------------------------------------
// Security
// ---------------------------------------------------------------------------
export const securityApi = {
  scanDevice: (deviceId: string) => api.post(`/api/security/scan/${deviceId}`),
  getVulnerabilities: (deviceId: string) => api.get(`/api/security/vulnerabilities/${deviceId}`),
};

// ---------------------------------------------------------------------------
// Intelligence
// ---------------------------------------------------------------------------
export const intelligenceApi = {
  getInsights: (networkId: string) => api.get(`/api/intelligence/insights/${networkId}`),
};

// ---------------------------------------------------------------------------
// WebSocket helper
// ---------------------------------------------------------------------------
export function createWebSocket(path = '/ws/updates'): WebSocket {
  const wsBase = BASE_URL.replace(/^http/, 'ws') || `ws://${window.location.host}`;
  return new WebSocket(`${wsBase}${path}`);
}

export default api;
