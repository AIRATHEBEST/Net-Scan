import React, { useState } from 'react';
import { Zap, Download, Upload, Activity, Play } from 'lucide-react';

const SpeedTest: React.FC = () => {
  const [isTesting, setIsTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState({
    download: 0,
    upload: 0,
    ping: 0
  });

  const runSpeedTest = async () => {
    setIsTesting(true);
    setProgress(0);
    
    // Simulate speed test
    const duration = 3000;
    const steps = 100;
    const interval = duration / steps;

    for (let i = 0; i <= steps; i++) {
      await new Promise(resolve => setTimeout(resolve, interval));
      setProgress((i / steps) * 100);
      
      if (i === steps) {
        // Generate realistic results
        setResults({
          download: Math.floor(Math.random() * 200) + 100,
          upload: Math.floor(Math.random() * 50) + 20,
          ping: Math.floor(Math.random() * 20) + 10
        });
      }
    }

    setIsTesting(false);
  };

  return (
    <div className="speed-test">
      <div className="speed-header">
        <div className="header-title">
          <Zap size={28} />
          <h2>Internet Speed Test</h2>
        </div>
        <p className="header-description">
          Test your internet connection speed and latency
        </p>
      </div>

      <div className="speed-content">
        <div className="speed-gauge">
          <div className="gauge-container">
            <svg viewBox="0 0 200 120" className="gauge-svg">
              <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="#2F2F2F"
                strokeWidth="20"
                strokeLinecap="round"
              />
              <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="20"
                strokeLinecap="round"
                strokeDasharray={`${progress * 2.51} 251`}
                className="gauge-progress"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#9E7FFF" />
                  <stop offset="100%" stopColor="#38bdf8" />
                </linearGradient>
              </defs>
            </svg>
            <div className="gauge-value">
              {isTesting ? (
                <>
                  <span className="testing-label">Testing...</span>
                  <span className="testing-progress">{Math.round(progress)}%</span>
                </>
              ) : results.download > 0 ? (
                <>
                  <span className="speed-value">{results.download}</span>
                  <span className="speed-unit">Mbps</span>
                </>
              ) : (
                <span className="ready-label">Ready</span>
              )}
            </div>
          </div>

          <button 
            className="test-button"
            onClick={runSpeedTest}
            disabled={isTesting}
          >
            <Play size={20} />
            <span>{isTesting ? 'Testing...' : 'Start Test'}</span>
          </button>
        </div>

        {results.download > 0 && !isTesting && (
          <div className="results-grid">
            <div className="result-card">
              <div className="result-icon download">
                <Download size={24} />
              </div>
              <div className="result-content">
                <div className="result-label">Download</div>
                <div className="result-value">{results.download} Mbps</div>
              </div>
            </div>

            <div className="result-card">
              <div className="result-icon upload">
                <Upload size={24} />
              </div>
              <div className="result-content">
                <div className="result-label">Upload</div>
                <div className="result-value">{results.upload} Mbps</div>
              </div>
            </div>

            <div className="result-card">
              <div className="result-icon ping">
                <Activity size={24} />
              </div>
              <div className="result-content">
                <div className="result-label">Ping</div>
                <div className="result-value">{results.ping} ms</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="speed-info">
        <h3>Understanding Your Results</h3>
        <div className="info-grid">
          <div className="info-card">
            <h4>Download Speed</h4>
            <p>Measures how fast data is transferred from the internet to your device. Higher is better for streaming and downloads.</p>
          </div>
          <div className="info-card">
            <h4>Upload Speed</h4>
            <p>Measures how fast data is transferred from your device to the internet. Important for video calls and file uploads.</p>
          </div>
          <div className="info-card">
            <h4>Ping (Latency)</h4>
            <p>Measures the time it takes for data to travel to a server and back. Lower is better for gaming and video calls.</p>
          </div>
        </div>
      </div>

      <style>{`
        .speed-test {
          max-width: 900px;
          margin: 0 auto;
        }

        .speed-header {
          text-align: center;
          margin-bottom: 48px;
        }

        .header-title {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          color: #9E7FFF;
          margin-bottom: 12px;
        }

        .header-title h2 {
          font-size: 32px;
          font-weight: 700;
          color: #FFFFFF;
        }

        .header-description {
          font-size: 16px;
          color: #A3A3A3;
        }

        .speed-content {
          background: #262626;
          border: 1px solid #2F2F2F;
          border-radius: 24px;
          padding: 48px;
          margin-bottom: 32px;
        }

        .speed-gauge {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 32px;
        }

        .gauge-container {
          position: relative;
          width: 280px;
          height: 180px;
        }

        .gauge-svg {
          width: 100%;
          height: 100%;
        }

        .gauge-progress {
          transition: stroke-dasharray 0.3s ease;
        }

        .gauge-value {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -20%);
          text-align: center;
        }

        .speed-value {
          display: block;
          font-size: 56px;
          font-weight: 700;
          color: #FFFFFF;
          line-height: 1;
        }

        .speed-unit {
          display: block;
          font-size: 18px;
          color: #A3A3A3;
          margin-top: 8px;
        }

        .testing-label {
          display: block;
          font-size: 18px;
          color: #9E7FFF;
          font-weight: 600;
        }

        .testing-progress {
          display: block;
          font-size: 32px;
          font-weight: 700;
          color: #FFFFFF;
          margin-top: 8px;
        }

        .ready-label {
          display: block;
          font-size: 24px;
          color: #A3A3A3;
          font-weight: 600;
        }

        .test-button {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px 48px;
          background: linear-gradient(135deg, #9E7FFF 0%, #7c3aed 100%);
          color: #FFFFFF;
          border-radius: 12px;
          font-size: 18px;
          font-weight: 600;
          transition: all 0.3s ease;
        }

        .test-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 12px 32px rgba(158, 127, 255, 0.4);
        }

        .test-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .results-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 20px;
          margin-top: 40px;
        }

        .result-card {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 20px;
          background: rgba(158, 127, 255, 0.05);
          border: 1px solid #2F2F2F;
          border-radius: 16px;
        }

        .result-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #FFFFFF;
        }

        .result-icon.download {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .result-icon.upload {
          background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        }

        .result-icon.ping {
          background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
        }

        .result-content {
          flex: 1;
        }

        .result-label {
          font-size: 14px;
          color: #A3A3A3;
          margin-bottom: 4px;
        }

        .result-value {
          font-size: 24px;
          font-weight: 700;
          color: #FFFFFF;
        }

        .speed-info {
          background: #262626;
          border: 1px solid #2F2F2F;
          border-radius: 24px;
          padding: 32px;
        }

        .speed-info h3 {
          font-size: 22px;
          font-weight: 600;
          color: #FFFFFF;
          margin-bottom: 24px;
        }

        .info-grid {
          display: grid;
          gap: 20px;
        }

        .info-card {
          padding: 20px;
          background: rgba(158, 127, 255, 0.05);
          border-left: 3px solid #9E7FFF;
          border-radius: 12px;
        }

        .info-card h4 {
          font-size: 16px;
          font-weight: 600;
          color: #FFFFFF;
          margin-bottom: 8px;
        }

        .info-card p {
          font-size: 14px;
          color: #A3A3A3;
          line-height: 1.6;
        }

        @media (max-width: 768px) {
          .speed-content {
            padding: 32px 24px;
          }

          .gauge-container {
            width: 220px;
            height: 140px;
          }

          .speed-value {
            font-size: 42px;
          }

          .results-grid {
            grid-template-columns: 1fr;
          }

          .speed-info {
            padding: 24px;
          }
        }
      `}</style>
    </div>
  );
};

export default SpeedTest;
