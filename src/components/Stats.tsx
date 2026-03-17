import React from 'react';
import { Wifi, Shield, AlertTriangle, Plus } from 'lucide-react';
import { Device } from '../types';

interface StatsProps {
  devices: Device[];
}

const Stats: React.FC<StatsProps> = ({ devices }) => {
  const stats = {
    total: devices.length,
    online: devices.filter(d => d.status === 'online').length,
    security: devices.filter(d => d.securityLevel === 'critical' || d.securityLevel === 'warning').length,
    new: devices.filter(d => d.isNew).length
  };

  const statCards = [
    { label: 'Total Devices', value: stats.total, icon: Wifi, color: '#9E7FFF' },
    { label: 'Online', value: stats.online, icon: Wifi, color: '#10b981' },
    { label: 'Security Issues', value: stats.security, icon: Shield, color: '#ef4444' },
    { label: 'New Devices', value: stats.new, icon: Plus, color: '#38bdf8' }
  ];

  return (
    <div className="stats-grid">
      {statCards.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div key={index} className="stat-card" style={{ '--accent-color': stat.color } as React.CSSProperties}>
            <div className="stat-icon">
              <Icon size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          </div>
        );
      })}

      <style jsx>{`
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 32px;
        }

        .stat-card {
          background: #262626;
          border: 1px solid #2F2F2F;
          border-radius: 16px;
          padding: 24px;
          display: flex;
          align-items: center;
          gap: 16px;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .stat-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 3px;
          background: var(--accent-color);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .stat-card:hover {
          transform: translateY(-4px);
          border-color: var(--accent-color);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        .stat-card:hover::before {
          opacity: 1;
        }

        .stat-icon {
          width: 56px;
          height: 56px;
          background: var(--accent-color);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #FFFFFF;
          opacity: 0.9;
        }

        .stat-content {
          flex: 1;
        }

        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: #FFFFFF;
          line-height: 1;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 14px;
          color: #A3A3A3;
          font-weight: 500;
        }

        @media (max-width: 768px) {
          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
          }

          .stat-card {
            padding: 20px;
          }

          .stat-icon {
            width: 48px;
            height: 48px;
          }

          .stat-value {
            font-size: 28px;
          }

          .stat-label {
            font-size: 13px;
          }
        }
      `}</style>
    </div>
  );
};

export default Stats;
