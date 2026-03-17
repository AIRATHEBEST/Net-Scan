import React from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, Lock, Unlock, Wifi } from 'lucide-react';
import { Device } from '../types';

interface SecurityDashboardProps {
  devices: Device[];
}

const SecurityDashboard: React.FC<SecurityDashboardProps> = ({ devices }) => {
  const securityIssues = [
    {
      id: '1',
      severity: 'critical' as const,
      title: 'Open SSH Port Detected',
      device: devices.find(d => d.openPorts.includes(22))?.name || 'Unknown Device',
      description: 'SSH port (22) is open and accessible from the network',
      recommendation: 'Close SSH port or restrict access to specific IP addresses'
    },
    {
      id: '2',
      severity: 'high' as const,
      title: 'Multiple Open Ports',
      device: devices.find(d => d.openPorts.length > 5)?.name || 'Unknown Device',
      description: 'Device has more than 5 open ports, increasing attack surface',
      recommendation: 'Review and close unnecessary ports'
    },
    {
      id: '3',
      severity: 'medium' as const,
      title: 'Outdated Firmware Detected',
      device: devices[2]?.name || 'Unknown Device',
      description: 'Device may be running outdated firmware',
      recommendation: 'Check for and install firmware updates'
    }
  ];

  const networkSecurity = {
    encryption: 'WPA3',
    strength: 'Strong',
    hiddenSSID: false,
    guestNetwork: true
  };

  const getSeverityColor = (severity: string) => {
    const colors = {
      critical: '#ef4444',
      high: '#f59e0b',
      medium: '#f59e0b',
      low: '#10b981'
    };
    return colors[severity as keyof typeof colors] || '#6b7280';
  };

  const getSeverityIcon = (severity: string) => {
    if (severity === 'critical' || severity === 'high') return <XCircle size={20} />;
    if (severity === 'medium') return <AlertTriangle size={20} />;
    return <CheckCircle size={20} />;
  };

  return (
    <div className="security-dashboard">
      <div className="security-header">
        <div className="header-title">
          <Shield size={28} />
          <h2>Security Dashboard</h2>
        </div>
        <div className="security-score">
          <div className="score-circle">
            <span className="score-value">78</span>
            <span className="score-label">Score</span>
          </div>
        </div>
      </div>

      <div className="security-grid">
        <div className="security-card network-info">
          <h3>
            <Wifi size={20} />
            Network Security
          </h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Encryption</span>
              <span className="info-value">
                <Lock size={16} />
                {networkSecurity.encryption}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Signal Strength</span>
              <span className="info-value">{networkSecurity.strength}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Hidden SSID</span>
              <span className="info-value">
                {networkSecurity.hiddenSSID ? <Lock size={16} /> : <Unlock size={16} />}
                {networkSecurity.hiddenSSID ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Guest Network</span>
              <span className="info-value">
                {networkSecurity.guestNetwork ? <CheckCircle size={16} color="#10b981" /> : <XCircle size={16} color="#ef4444" />}
                {networkSecurity.guestNetwork ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>

        <div className="security-card">
          <h3>
            <AlertTriangle size={20} />
            Security Issues ({securityIssues.length})
          </h3>
          <div className="issues-list">
            {securityIssues.map(issue => (
              <div key={issue.id} className="issue-item">
                <div className="issue-header">
                  <div 
                    className="issue-severity"
                    style={{ color: getSeverityColor(issue.severity) }}
                  >
                    {getSeverityIcon(issue.severity)}
                    <span>{issue.severity.toUpperCase()}</span>
                  </div>
                  <div className="issue-device">{issue.device}</div>
                </div>
                <h4>{issue.title}</h4>
                <p className="issue-description">{issue.description}</p>
                <div className="issue-recommendation">
                  <strong>Recommendation:</strong> {issue.recommendation}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="recommendations-card">
        <h3>
          <CheckCircle size={20} />
          Security Recommendations
        </h3>
        <ul className="recommendations-list">
          <li>Enable WPA3 encryption if your router supports it</li>
          <li>Change default router admin credentials</li>
          <li>Enable firewall on all devices</li>
          <li>Regularly update device firmware</li>
          <li>Use strong, unique passwords for all devices</li>
          <li>Disable UPnP if not needed</li>
          <li>Enable MAC address filtering</li>
          <li>Set up a separate guest network for visitors</li>
        </ul>
      </div>

      <style>{`
        .security-dashboard {
          max-width: 1200px;
        }

        .security-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 32px;
          flex-wrap: wrap;
          gap: 24px;
        }

        .header-title {
          display: flex;
          align-items: center;
          gap: 12px;
          color: #9E7FFF;
        }

        .header-title h2 {
          font-size: 28px;
          font-weight: 700;
          color: #FFFFFF;
        }

        .security-score {
          background: linear-gradient(135deg, #9E7FFF 0%, #7c3aed 100%);
          padding: 24px;
          border-radius: 16px;
          box-shadow: 0 8px 24px rgba(158, 127, 255, 0.3);
        }

        .score-circle {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
        }

        .score-value {
          font-size: 48px;
          font-weight: 700;
          color: #FFFFFF;
          line-height: 1;
        }

        .score-label {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.8);
          font-weight: 500;
        }

        .security-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
          gap: 24px;
          margin-bottom: 24px;
        }

        .security-card {
          background: #262626;
          border: 1px solid #2F2F2F;
          border-radius: 16px;
          padding: 24px;
        }

        .security-card h3 {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 18px;
          font-weight: 600;
          color: #FFFFFF;
          margin-bottom: 20px;
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
        }

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .info-label {
          font-size: 13px;
          color: #A3A3A3;
          font-weight: 500;
        }

        .info-value {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 15px;
          color: #FFFFFF;
          font-weight: 600;
        }

        .issues-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .issue-item {
          padding: 16px;
          background: rgba(158, 127, 255, 0.05);
          border: 1px solid #2F2F2F;
          border-radius: 12px;
        }

        .issue-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .issue-severity {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.5px;
        }

        .issue-device {
          font-size: 13px;
          color: #A3A3A3;
        }

        .issue-item h4 {
          font-size: 16px;
          font-weight: 600;
          color: #FFFFFF;
          margin-bottom: 8px;
        }

        .issue-description {
          font-size: 14px;
          color: #A3A3A3;
          margin-bottom: 12px;
          line-height: 1.5;
        }

        .issue-recommendation {
          padding: 12px;
          background: rgba(158, 127, 255, 0.1);
          border-left: 3px solid #9E7FFF;
          border-radius: 6px;
          font-size: 14px;
          color: #FFFFFF;
          line-height: 1.5;
        }

        .issue-recommendation strong {
          color: #9E7FFF;
        }

        .recommendations-card {
          background: #262626;
          border: 1px solid #2F2F2F;
          border-radius: 16px;
          padding: 24px;
        }

        .recommendations-card h3 {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 18px;
          font-weight: 600;
          color: #FFFFFF;
          margin-bottom: 20px;
        }

        .recommendations-list {
          list-style: none;
          display: grid;
          gap: 12px;
        }

        .recommendations-list li {
          padding: 12px 16px;
          background: rgba(158, 127, 255, 0.05);
          border-left: 3px solid #9E7FFF;
          border-radius: 8px;
          font-size: 14px;
          color: #FFFFFF;
          line-height: 1.5;
        }

        @media (max-width: 1024px) {
          .security-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 768px) {
          .security-header {
            flex-direction: column;
            align-items: stretch;
          }

          .security-score {
            text-align: center;
          }

          .info-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default SecurityDashboard;
