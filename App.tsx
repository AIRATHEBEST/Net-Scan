import React, { useState, useEffect } from 'react';
import { Wifi, Shield, Activity, Zap, Search, AlertTriangle, CheckCircle, XCircle, Smartphone, Laptop, Tv, Camera, Router, HardDrive, RefreshCw, Play, Pause } from 'lucide-react';
import NetworkScanner from './components/NetworkScanner';
import DeviceList from './components/DeviceList';
import SecurityDashboard from './components/SecurityDashboard';
import SpeedTest from './components/SpeedTest';
import Header from './components/Header';
import Stats from './components/Stats';
import { Device } from './types';
import { generateMockDevices } from './utils/mockData';

function App() {
  const [activeTab, setActiveTab] = useState<'scanner' | 'security' | 'speed'>('scanner');
  const [devices, setDevices] = useState<Device[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [autoScan, setAutoScan] = useState(false);

  useEffect(() => {
    // Initial scan
    performScan();
  }, []);

  useEffect(() => {
    if (autoScan) {
      const interval = setInterval(() => {
        performScan();
      }, 30000); // Scan every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoScan]);

  const performScan = async () => {
    setIsScanning(true);
    setScanProgress(0);

    // Simulate scanning progress
    const progressInterval = setInterval(() => {
      setScanProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    // Simulate network scan
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const newDevices = generateMockDevices();
    setDevices(newDevices);
    setIsScanning(false);
    setScanProgress(100);
  };

  const tabs = [
    { id: 'scanner' as const, label: 'Network Scanner', icon: Wifi },
    { id: 'security' as const, label: 'Security', icon: Shield },
    { id: 'speed' as const, label: 'Speed Test', icon: Zap }
  ];

  return (
    <div className="app">
      <Header />
      
      <nav className="nav-tabs">
        <div className="nav-container">
          {tabs.map(tab => {
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
        
        {activeTab === 'security' && (
          <SecurityDashboard devices={devices} />
        )}
        
        {activeTab === 'speed' && (
          <SpeedTest />
        )}
      </main>

      <style jsx>{`
        .app {
          min-height: 100vh;
          background: #171717;
        }

        .nav-tabs {
          background: #262626;
          border-bottom: 1px solid #2F2F2F;
          position: sticky;
          top: 0;
          z-index: 100;
          backdrop-filter: blur(10px);
        }

        .nav-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 24px;
          display: flex;
          gap: 8px;
        }

        .nav-tab {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 16px 24px;
          background: transparent;
          color: #A3A3A3;
          font-size: 15px;
          font-weight: 500;
          border-bottom: 2px solid transparent;
          transition: all 0.2s ease;
          position: relative;
        }

        .nav-tab:hover {
          color: #FFFFFF;
          background: rgba(158, 127, 255, 0.1);
        }

        .nav-tab.active {
          color: #9E7FFF;
          border-bottom-color: #9E7FFF;
        }

        .main-content {
          max-width: 1400px;
          margin: 0 auto;
          padding: 32px 24px;
        }

        @media (max-width: 768px) {
          .nav-container {
            padding: 0 16px;
          }

          .nav-tab {
            padding: 12px 16px;
            font-size: 14px;
          }

          .nav-tab span {
            display: none;
          }

          .main-content {
            padding: 24px 16px;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
