import React, { useState } from 'react';
import { Smartphone, Laptop, Tv, Camera, Router, HardDrive, Tablet, AlertTriangle, CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Device, DeviceType } from '../types';

interface DeviceListProps {
  devices: Device[];
}

const DeviceList: React.FC<DeviceListProps> = ({ devices }) => {
  const [expandedDevice, setExpandedDevice] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'online' | 'offline' | 'issues'>('all');

  const getDeviceIcon = (type: DeviceType) => {
    const icons = {
      smartphone: Smartphone,
      laptop: Laptop,
      tablet: Tablet,
      tv: Tv,
      camera: Camera,
      router: Router,
      iot: HardDrive,
      desktop: Laptop,
      unknown: HardDrive
    };
    return icons[type] || HardDrive;
  };

  const getSecurityIcon = (level: string) => {
    if (level === 'secure') return <CheckCircle size={18} color="#10b981" />;
    if (level === 'warning') return <AlertTriangle size={18} color="#f59e0b" />;
    return <XCircle size={18} color="#ef4444" />;
  };

  const filteredDevices = devices.filter(device => {
    if (filter === 'online') return device.status === 'online';
    if (filter === 'offline') return device.status === 'offline';
    if (filter === 'issues') return device.securityLevel !== 'secure';
    return true;
  });

  return (
    <div className="device-list-container">
      <div className="list-header">
        <h2>Discovered Devices ({filteredDevices.length})</h2>
        <div className="filter-buttons">
          <button 
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={filter === 'online' ? 'active' : ''}
            onClick={() => setFilter('online')}
          >
            Online
          </button>
          <button 
            className={filter === 'offline' ? 'active' : ''}
            onClick={() => setFilter('offline')}
          >
            Offline
          </button>
          <button 
            className={filter === 'issues' ? 'active' : ''}
            onClick={() => setFilter('issues')}
          >
            Issues
          </button>
        </div>
      </div>

      <div className="devices-grid">
        {filteredDevices.map(device => {
          const Icon = getDeviceIcon(device.type);
          const isExpanded = expandedDevice === device.id;

          return (
            <div 
              key={device.id} 
              className={`device-card ${device.isNew ? 'new' : ''}`}
              onClick={() => setExpandedDevice(isExpanded ? null : device.id)}
            >
              {device.isNew && <div className="new-badge">NEW</div>}
              
              <div className="device-main">
                <div className="device-icon">
                  <Icon size={24} />
                </div>
                <div className="device-info">
                  <div className="device-name">{device.name}</div>
                  <div className="device-vendor">{device.vendor}</div>
                </div>
                <div className="device-status">
                  <div className={`status-indicator ${device.status}`}></div>
                  {getSecurityIcon(device.securityLevel)}
                </div>
              </div>

              <div className="device-details">
                <div className="detail-row">
                  <span className="detail-label">IP Address:</span>
                  <span className="detail-value">{device.ip}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">MAC Address:</span>
                  <span className="detail-value">{device.mac}</span>
                </div>
                {device.os && (
                  <div className="detail-row">
                    <span className="detail-label">Operating System:</span>
                    <span className="detail-value">{device.os}</span>
                  </div>
                )}
              </div>

              {isExpanded && (
                <div className="device-expanded">
                  <div className="expanded-section">
                    <h4>Open Ports</h4>
                    <div className="ports-list">
                      {device.openPorts.map(port => (
                        <span key={port} className="port-badge">{port}</span>
                      ))}
                    </div>
                  </div>
                  <div className="expanded-section">
                    <h4>Services</h4>
                    <div className="services-list">
                      {device.services.map(service => (
                        <span key={service} className="service-badge">{service}</span>
                      ))}
                    </div>
                  </div>
                  <div className="expanded-section">
                    <h4>Last Seen</h4>
                    <p className="last-seen">{device.lastSeen.toLocaleString()}</p>
                  </div>
                </div>
              )}

              <button className="expand-btn">
                {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </button>
            </div>
          );
        })}
      </div>

      <style jsx>{`
        .device-list-container {
          margin-top: 24px;
        }

        .list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          flex-wrap: wrap;
          gap: 16px;
        }

        .list-header h2 {
          font-size: 22px;
          font-weight: 600;
          color: #FFFFFF;
        }

        .filter-buttons {
          display: flex;
          gap: 8px;
          background: #262626;
          padding: 4px;
          border-radius: 10px;
          border: 1px solid #2F2F2F;
        }

        .filter-buttons button {
          padding: 8px 16px;
          background: transparent;
          color: #A3A3A3;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s ease;
        }

        .filter-buttons button:hover {
          color: #FFFFFF;
          background: rgba(158, 127, 255, 0.1);
        }

        .filter-buttons button.active {
          background: #9E7FFF;
          color: #FFFFFF;
        }

        .devices-grid {
          display: grid;
          gap: 16px;
        }

        .device-card {
          background: #262626;
          border: 1px solid #2F2F2F;
          border-radius: 16px;
          padding: 20px;
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
        }

        .device-card.new {
          border-color: #38bdf8;
          box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
        }

        .device-card:hover {
          transform: translateY(-2px);
          border-color: #9E7FFF;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        .new-badge {
          position: absolute;
          top: 12px;
          right: 12px;
          background: #38bdf8;
          color: #FFFFFF;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.5px;
        }

        .device-main {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .device-icon {
          width: 56px;
          height: 56px;
          background: rgba(158, 127, 255, 0.1);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #9E7FFF;
        }

        .device-info {
          flex: 1;
        }

        .device-name {
          font-size: 16px;
          font-weight: 600;
          color: #FFFFFF;
          margin-bottom: 4px;
        }

        .device-vendor {
          font-size: 14px;
          color: #A3A3A3;
        }

        .device-status {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }

        .status-indicator.online {
          background: #10b981;
          box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        }

        .status-indicator.offline {
          background: #6b7280;
        }

        .device-details {
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid #2F2F2F;
          display: grid;
          gap: 8px;
        }

        .detail-row {
          display: flex;
          justify-content: space-between;
          font-size: 14px;
        }

        .detail-label {
          color: #A3A3A3;
        }

        .detail-value {
          color: #FFFFFF;
          font-weight: 500;
        }

        .device-expanded {
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid #2F2F2F;
        }

        .expanded-section {
          margin-bottom: 16px;
        }

        .expanded-section:last-child {
          margin-bottom: 0;
        }

        .expanded-section h4 {
          font-size: 14px;
          font-weight: 600;
          color: #A3A3A3;
          margin-bottom: 8px;
        }

        .ports-list,
        .services-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .port-badge,
        .service-badge {
          padding: 4px 12px;
          background: rgba(158, 127, 255, 0.1);
          border: 1px solid rgba(158, 127, 255, 0.3);
          border-radius: 6px;
          font-size: 13px;
          color: #9E7FFF;
          font-weight: 500;
        }

        .service-badge {
          background: rgba(56, 189, 248, 0.1);
          border-color: rgba(56, 189, 248, 0.3);
          color: #38bdf8;
        }

        .last-seen {
          font-size: 14px;
          color: #FFFFFF;
        }

        .expand-btn {
          position: absolute;
          bottom: 12px;
          right: 12px;
          width: 32px;
          height: 32px;
          background: rgba(158, 127, 255, 0.1);
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #9E7FFF;
          transition: all 0.2s ease;
        }

        .expand-btn:hover {
          background: rgba(158, 127, 255, 0.2);
        }

        @media (max-width: 768px) {
          .list-header {
            flex-direction: column;
            align-items: stretch;
          }

          .filter-buttons {
            width: 100%;
            justify-content: space-between;
          }

          .filter-buttons button {
            flex: 1;
            padding: 8px;
            font-size: 13px;
          }

          .device-card {
            padding: 16px;
          }

          .device-icon {
            width: 48px;
            height: 48px;
          }
        }
      `}</style>
    </div>
  );
};

export default DeviceList;
