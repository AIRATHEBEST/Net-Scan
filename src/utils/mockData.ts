import { Device, DeviceType, SecurityLevel } from '../types';

const deviceNames = [
  "John's iPhone 14 Pro",
  "MacBook Pro",
  "Living Room TV",
  "Ring Doorbell",
  "TP-Link Router",
  "iPad Air",
  "Samsung Galaxy S23",
  "Google Nest Hub",
  "PlayStation 5",
  "HP Printer",
  "Sonos Speaker",
  "Philips Hue Bridge",
  "Dell Desktop",
  "Apple Watch",
  "Amazon Echo"
];

const vendors = [
  'Apple Inc.',
  'Samsung Electronics',
  'Google LLC',
  'Amazon Technologies',
  'TP-Link Technologies',
  'Dell Inc.',
  'HP Inc.',
  'Sony Corporation',
  'Philips',
  'Ring Inc.',
  'Sonos Inc.',
  'Nest Labs'
];

const deviceTypes: DeviceType[] = ['smartphone', 'laptop', 'tablet', 'tv', 'camera', 'router', 'iot', 'desktop'];

const commonPorts = [
  [80, 443], // Web
  [22, 80, 443], // Server
  [554, 8080], // Camera
  [53, 80, 443], // Router
  [80], // IoT
  [5353, 8009], // Smart devices
];

const services = [
  ['HTTP', 'HTTPS'],
  ['SSH', 'HTTP', 'HTTPS'],
  ['RTSP', 'HTTP'],
  ['DNS', 'HTTP', 'HTTPS'],
  ['HTTP'],
  ['mDNS', 'Chromecast']
];

function generateIP(): string {
  return `192.168.1.${Math.floor(Math.random() * 254) + 1}`;
}

function generateMAC(): string {
  return Array.from({ length: 6 }, () => 
    Math.floor(Math.random() * 256).toString(16).padStart(2, '0')
  ).join(':').toUpperCase();
}

function getSecurityLevel(openPorts: number[]): SecurityLevel {
  if (openPorts.includes(22) || openPorts.includes(23) || openPorts.includes(3389)) {
    return 'critical';
  }
  if (openPorts.length > 5) {
    return 'warning';
  }
  return 'secure';
}

export function generateMockDevices(): Device[] {
  const deviceCount = Math.floor(Math.random() * 5) + 8; // 8-12 devices
  const devices: Device[] = [];
  const usedIPs = new Set<string>();

  for (let i = 0; i < deviceCount; i++) {
    let ip = generateIP();
    while (usedIPs.has(ip)) {
      ip = generateIP();
    }
    usedIPs.add(ip);

    const type = deviceTypes[Math.floor(Math.random() * deviceTypes.length)];
    const portIndex = Math.floor(Math.random() * commonPorts.length);
    const openPorts = commonPorts[portIndex];
    const isOnline = Math.random() > 0.1; // 90% online

    const device: Device = {
      id: `device-${i}`,
      name: deviceNames[i % deviceNames.length],
      ip,
      mac: generateMAC(),
      vendor: vendors[Math.floor(Math.random() * vendors.length)],
      type,
      status: isOnline ? 'online' : 'offline',
      lastSeen: new Date(Date.now() - Math.random() * 3600000),
      openPorts,
      services: services[portIndex],
      os: type === 'laptop' || type === 'desktop' ? (Math.random() > 0.5 ? 'Windows 11' : 'macOS 14') : undefined,
      securityLevel: getSecurityLevel(openPorts),
      isNew: Math.random() > 0.8 // 20% chance of being new
    };

    devices.push(device);
  }

  return devices.sort((a, b) => a.ip.localeCompare(b.ip));
}
