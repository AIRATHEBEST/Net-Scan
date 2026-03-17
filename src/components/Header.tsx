import React from 'react';
import { Wifi, Shield, Activity } from 'lucide-react';

interface HeaderProps {
  apiConnected?: boolean;
}

const Header: React.FC<HeaderProps> = ({ apiConnected = false }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">
            <Wifi size={24} />
          </div>
          <h1>NetScan</h1>
        </div>
        <div className="network-info">
          <div className="network-badge">
            <Shield size={16} />
            <span>Home Network</span>
          </div>
          <div className={`api-status ${apiConnected ? 'connected' : 'demo'}`}>
            <Activity size={14} />
            <span>{apiConnected ? 'Live API' : 'Demo Mode'}</span>
          </div>
          <div className="network-status">
            <div className="status-dot"></div>
            <span>Connected</span>
          </div>
        </div>
      </div>
      <style>{`
        .header {
          background: linear-gradient(135deg, #9E7FFF 0%, #7c3aed 100%);
          padding: 24px;
          box-shadow: 0 4px 20px rgba(158, 127, 255, 0.3);
        }
        .header-content {
          max-width: 1400px;
          margin: 0 auto;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .logo-icon {
          width: 48px;
          height: 48px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          backdrop-filter: blur(10px);
        }
        .logo h1 {
          font-size: 28px;
          font-weight: 700;
          color: #FFFFFF;
          letter-spacing: -0.5px;
        }
        .network-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .network-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 20px;
          font-size: 14px;
          font-weight: 500;
          color: #FFFFFF;
          backdrop-filter: blur(10px);
        }
        .api-status {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          backdrop-filter: blur(10px);
        }
        .api-status.connected {
          background: rgba(16, 185, 129, 0.3);
          color: #6ee7b7;
          border: 1px solid rgba(16, 185, 129, 0.4);
        }
        .api-status.demo {
          background: rgba(245, 158, 11, 0.3);
          color: #fcd34d;
          border: 1px solid rgba(245, 158, 11, 0.4);
        }
        .network-status {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #FFFFFF;
          font-size: 14px;
          font-weight: 500;
        }
        .status-dot {
          width: 8px;
          height: 8px;
          background: #10b981;
          border-radius: 50%;
          animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.2); }
        }
        @media (max-width: 768px) {
          .header { padding: 16px; }
          .logo h1 { font-size: 24px; }
          .logo-icon { width: 40px; height: 40px; }
          .network-badge span { display: none; }
          .api-status span { display: none; }
          .network-status { font-size: 13px; }
        }
      `}</style>
    </header>
  );
};

export default Header;
