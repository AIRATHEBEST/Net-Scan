import React from 'react';
import { Search, RefreshCw, Play, Pause } from 'lucide-react';

interface NetworkScannerProps {
  isScanning: boolean;
  scanProgress: number;
  onScan: () => void;
  autoScan: boolean;
  onAutoScanToggle: () => void;
}

const NetworkScanner: React.FC<NetworkScannerProps> = ({
  isScanning,
  scanProgress,
  onScan,
  autoScan,
  onAutoScanToggle
}) => {
  return (
    <div className="scanner-container">
      <div className="scanner-header">
        <div className="scanner-title">
          <Search size={24} />
          <h2>Network Scanner</h2>
        </div>
        <div className="scanner-actions">
          <button 
            className={`auto-scan-btn ${autoScan ? 'active' : ''}`}
            onClick={onAutoScanToggle}
          >
            {autoScan ? <Pause size={18} /> : <Play size={18} />}
            <span>Auto Scan</span>
          </button>
          <button 
            className="scan-btn"
            onClick={onScan}
            disabled={isScanning}
          >
            <RefreshCw size={18} className={isScanning ? 'spinning' : ''} />
            <span>{isScanning ? 'Scanning...' : 'Scan Network'}</span>
          </button>
        </div>
      </div>

      {isScanning && (
        <div className="progress-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${scanProgress}%` }}></div>
          </div>
          <div className="progress-text">
            Scanning network: {scanProgress}%
          </div>
        </div>
      )}

      <style>{`
        .scanner-container {
          background: #262626;
          border: 1px solid #2F2F2F;
          border-radius: 16px;
          padding: 24px;
          margin-bottom: 24px;
        }

        .scanner-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 16px;
        }

        .scanner-title {
          display: flex;
          align-items: center;
          gap: 12px;
          color: #9E7FFF;
        }

        .scanner-title h2 {
          font-size: 20px;
          font-weight: 600;
          color: #FFFFFF;
        }

        .scanner-actions {
          display: flex;
          gap: 12px;
        }

        .auto-scan-btn,
        .scan-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 20px;
          border-radius: 10px;
          font-size: 14px;
          font-weight: 600;
          transition: all 0.2s ease;
        }

        .auto-scan-btn {
          background: #262626;
          color: #A3A3A3;
          border: 1px solid #2F2F2F;
        }

        .auto-scan-btn.active {
          background: rgba(158, 127, 255, 0.1);
          color: #9E7FFF;
          border-color: #9E7FFF;
        }

        .auto-scan-btn:hover {
          background: rgba(158, 127, 255, 0.1);
          border-color: #9E7FFF;
          color: #9E7FFF;
        }

        .scan-btn {
          background: linear-gradient(135deg, #9E7FFF 0%, #7c3aed 100%);
          color: #FFFFFF;
          border: none;
        }

        .scan-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(158, 127, 255, 0.4);
        }

        .scan-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .spinning {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        .progress-container {
          margin-top: 20px;
        }

        .progress-bar {
          width: 100%;
          height: 8px;
          background: #2F2F2F;
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #9E7FFF 0%, #38bdf8 100%);
          transition: width 0.3s ease;
          border-radius: 4px;
        }

        .progress-text {
          margin-top: 8px;
          font-size: 14px;
          color: #A3A3A3;
          text-align: center;
        }

        @media (max-width: 768px) {
          .scanner-container {
            padding: 20px;
          }

          .scanner-header {
            flex-direction: column;
            align-items: stretch;
          }

          .scanner-actions {
            width: 100%;
          }

          .auto-scan-btn,
          .scan-btn {
            flex: 1;
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default NetworkScanner;
