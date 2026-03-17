export type DeviceType = 'smartphone' | 'laptop' | 'tablet' | 'tv' | 'camera' | 'router' | 'iot' | 'desktop' | 'unknown';

export type SecurityLevel = 'secure' | 'warning' | 'critical';

export interface Device {
  id: string;
  name: string;
  ip: string;
  mac: string;
  vendor: string;
  type: DeviceType;
  status: 'online' | 'offline';
  lastSeen: Date;
  openPorts: number[];
  services: string[];
  os?: string;
  securityLevel: SecurityLevel;
  isNew?: boolean;
}

export interface NetworkStats {
  totalDevices: number;
  onlineDevices: number;
  securityIssues: number;
  newDevices: number;
}

export interface SpeedTestResult {
  download: number;
  upload: number;
  ping: number;
  timestamp: Date;
}

export interface SecurityIssue {
  id: string;
  deviceId: string;
  deviceName: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  description: string;
  recommendation: string;
}
