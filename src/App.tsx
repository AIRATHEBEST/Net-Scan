import { useState, useEffect, useCallback } from 'react';
import { Wifi, Shield, Zap, LogOut } from 'lucide-react';
import NetworkScanner from './components/NetworkScanner';
import DeviceList from './components/DeviceList';
import SecurityDashboard from './components/SecurityDashboard';
import SpeedTest from './components/SpeedTest';
import Header from './components/Header';
import Stats from './components/Stats';
import Login from './components/Login';
import { Device } from './types';
import { generateMockDevices } from './utils/mockData';
import { devicesApi, networksApi, scanApi, createWebSocket } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState<'scanner' | 'security' | 'speed'>('scanner');
  const [devices, setDevices] = useState<Device[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [autoScan, setAutoScan] = useState(false);
  const [networkId, setNetworkId] = useState<string | null>(null);
  const [apiConnected, setApiConnected] = useState(false);

  // Check if user is already authenticated
  useEffect(() => {
    const token = localStorage.getItem('netscan_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('netscan_token');
    setIsAuthenticated(false);
    setDevices([]);
    setNetworkId(null);
    setApiConnected(false);
  };

  // Bootstrap: try backend, fall back to mock data
  useEffect(() => {
    if (!isAuthenticated) return;
    const init = async () => {
      try {
        const res = await networksApi.list();
        const nets: any[] = res.data.networks ?? [];
        if (nets.length > 0) setNetworkId(nets[0].id);
        setApiConnected(true);
        await loadDevicesFromApi(nets[0]?.id);
      } catch {
        setApiConnected(false);
        setDevices(generateMockDevices());
      }
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  // WebSocket for real-time updates
  useEffect(() => {
    if (!apiConnected) return;
    let ws: WebSocket;
    try {
      ws = createWebSocket();
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'scan_update') loadDevicesFromApi(networkId ?? undefined);
        } catch { /* ignore */ }
      };
    } catch { /* ignore */ }
    return () => ws?.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiConnected, networkId]);

  // Auto-scan interval
  useEffect(() => {
    if (!autoScan) return;
    const interval = setInterval(() => performScan(), 30_000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoScan, networkId, apiConnected]);

  const loadDevicesFromApi = useCallback(async (netId?: string) => {
    try {
      const res = await devicesApi.list(netId);
      const raw: any[] = res.data.devices ?? [];
      const mapped: Device[] = raw.map((d) => ({
        id: d.id,
        name: d.name,
        ip: d.ip,
        mac: d.mac,
        vendor: d.vendor ?? 'Unknown',
        type: d.type ?? 'unknown',
        status: d.status ?? 'online',
        lastSeen: new Date(d.lastSeen),
        openPorts: d.openPorts ?? [],
        services: d.services ?? [],
        os: d.os,
        securityLevel: d.securityLevel ?? 'secure',
        isNew: d.isNew ?? false,
      }));
      setDevices(mapped);
    } catch { /* keep existing */ }
  }, []);

  const performScan = useCallback(async () => {
    setIsScanning(true);
    setScanProgress(0);
    const progressInterval = setInterval(() => {
      setScanProgress((prev) => {
        if (prev >= 90) { clearInterval(progressInterval); return 90; }
        return prev + 10;
      });
    }, 200);
    try {
      if (apiConnected && networkId) {
        await scanApi.startNetworkScan(networkId);
        await loadDevicesFromApi(networkId);
      } else {
        await new Promise((r) => setTimeout(r, 2000));
        setDevices(generateMockDevices());
      }
    } catch {
      setDevices(generateMockDevices());
    } finally {
      clearInterval(progressInterval);
      setScanProgress(100);
      setIsScanning(false);
    }
  }, [apiConnected, networkId, loadDevicesFromApi]);

  // Initial scan
  useEffect(() => {
    if (!isAuthenticated) return;
    performScan();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const tabs = [
    { id: 'scanner' as const, label: 'Network Scanner', icon: Wifi },
    { id: 'security' as const, label: 'Security', icon: Shield },
    { id: 'speed' as const, label: 'Speed Test', icon: Zap },
  ];

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="app">
      <Header apiConnected={apiConnected} />
      <nav className="nav-tabs">
        <div className="nav-container">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={20} />
                <span>{tab.label}</span>
              </button>
            );
          })}
          <button className="logout-btn" onClick={handleLogout} title="Logout">
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </nav>
      <main className="main-content">
        {activeTab === 'scanner' && (
          <>
            <Stats devices={devices} />
            <NetworkScanner
              isScanning={isScanning}
              scanProgress={scanProgress}
              onScan={performScan}
              autoScan={autoScan}
              onAutoScanToggle={() => setAutoScan(!autoScan)}
            />
            <DeviceList devices={devices} />
          </>
        )}
        {activeTab === 'security' && <SecurityDashboard devices={devices} />}
        {activeTab === 'speed' && <SpeedTest />}
      </main>
      <style>{`
        .app { min-height: 100vh; background: #171717; }
        .nav-tabs { background: #262626; border-bottom: 1px solid #2F2F2F; position: sticky; top: 0; z-index: 100; backdrop-filter: blur(10px); }
        .nav-container { max-width: 1400px; margin: 0 auto; padding: 0 24px; display: flex; gap: 8px; align-items: center; }
        .nav-tab { display: flex; align-items: center; gap: 8px; padding: 16px 24px; background: transparent; color: #A3A3A3; font-size: 15px; font-weight: 500; border-bottom: 2px solid transparent; transition: all 0.2s ease; }
        .nav-tab:hover { color: #FFFFFF; background: rgba(158,127,255,0.1); }
        .nav-tab.active { color: #9E7FFF; border-bottom-color: #9E7FFF; }
        .logout-btn { display: flex; align-items: center; gap: 8px; padding: 16px 24px; background: transparent; color: #A3A3A3; font-size: 15px; font-weight: 500; border-bottom: 2px solid transparent; transition: all 0.2s ease; margin-left: auto; border: none; cursor: pointer; }
        .logout-btn:hover { color: #ef4444; background: rgba(239, 68, 68, 0.1); }
        .main-content { max-width: 1400px; margin: 0 auto; padding: 32px 24px; }
        @media (max-width: 768px) {
          .nav-container { padding: 0 16px; }
          .nav-tab { padding: 12px 16px; font-size: 14px; }
          .nav-tab span { display: none; }
          .logout-btn { padding: 12px 16px; }
          .logout-btn span { display: none; }
          .main-content { padding: 24px 16px; }
        }
      `}</style>
    </div>
  );
}

export default App;
