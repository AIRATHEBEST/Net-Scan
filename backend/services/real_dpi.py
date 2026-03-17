import asyncio
import logging
from typing import Dict, List, Optional
from scapy.all import sniff, IP, TCP, UDP, DNS, DNSQR, DNSRR, Raw
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.tls.record import TLS
from datetime import datetime
import re
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class RealDPIEngine:
    """
    🧪 Tier 1 Feature #5: Real DPI (Deep Packet Inspection)
    
    Not just a framework - ACTUAL protocol parsing:
    - DNS query logging and analysis
    - HTTP/HTTPS traffic inspection
    - SNI extraction from TLS handshakes
    - Application detection (Netflix, Zoom, YouTube, etc.)
    - Bandwidth per application
    - Traffic pattern analysis
    
    Goal: "Netflix streaming" not just "HTTPS traffic"
    """
    
    def __init__(self):
        self.application_signatures = self._load_application_signatures()
        self.dns_cache = {}
        self.traffic_patterns = defaultdict(lambda: {
            'bytes_sent': 0,
            'bytes_received': 0,
            'connections': [],
            'protocols': set(),
            'applications': set()
        })
        self.is_capturing = False
    
    def _load_application_signatures(self) -> Dict:
        """Load application detection signatures"""
        return {
            'streaming': {
                'netflix': {
                    'domains': [
                        'netflix.com', 'nflxvideo.net', 'nflximg.net', 
                        'nflxext.com', 'nflxso.net'
                    ],
                    'sni_patterns': [r'.*\.netflix\.com', r'.*\.nflxvideo\.net'],
                    'ports': [443],
                    'traffic_pattern': 'high_download'
                },
                'youtube': {
                    'domains': [
                        'youtube.com', 'googlevideo.com', 'ytimg.com'
                    ],
                    'sni_patterns': [r'.*\.youtube\.com', r'.*\.googlevideo\.com'],
                    'ports': [443],
                    'traffic_pattern': 'high_download'
                },
                'twitch': {
                    'domains': ['twitch.tv', 'ttvnw.net'],
                    'sni_patterns': [r'.*\.twitch\.tv'],
                    'ports': [443],
                    'traffic_pattern': 'high_download'
                },
                'spotify': {
                    'domains': ['spotify.com', 'scdn.co'],
                    'sni_patterns': [r'.*\.spotify\.com'],
                    'ports': [443, 4070],
                    'traffic_pattern': 'medium_download'
                }
            },
            'video_conferencing': {
                'zoom': {
                    'domains': ['zoom.us', 'zoom.com'],
                    'sni_patterns': [r'.*\.zoom\.us'],
                    'ports': [443, 8801, 8802],
                    'traffic_pattern': 'bidirectional'
                },
                'teams': {
                    'domains': ['teams.microsoft.com', 'skype.com'],
                    'sni_patterns': [r'.*\.teams\.microsoft\.com'],
                    'ports': [443],
                    'traffic_pattern': 'bidirectional'
                },
                'meet': {
                    'domains': ['meet.google.com', 'hangouts.google.com'],
                    'sni_patterns': [r'.*\.meet\.google\.com'],
                    'ports': [443],
                    'traffic_pattern': 'bidirectional'
                }
            },
            'social_media': {
                'facebook': {
                    'domains': ['facebook.com', 'fbcdn.net', 'instagram.com'],
                    'sni_patterns': [r'.*\.facebook\.com', r'.*\.instagram\.com'],
                    'ports': [443],
                    'traffic_pattern': 'mixed'
                },
                'twitter': {
                    'domains': ['twitter.com', 'twimg.com', 'x.com'],
                    'sni_patterns': [r'.*\.twitter\.com', r'.*\.x\.com'],
                    'ports': [443],
                    'traffic_pattern': 'mixed'
                },
                'tiktok': {
                    'domains': ['tiktok.com', 'tiktokcdn.com'],
                    'sni_patterns': [r'.*\.tiktok\.com'],
                    'ports': [443],
                    'traffic_pattern': 'high_download'
                }
            },
            'gaming': {
                'steam': {
                    'domains': ['steampowered.com', 'steamcontent.com'],
                    'sni_patterns': [r'.*\.steampowered\.com'],
                    'ports': [443, 27015, 27016],
                    'traffic_pattern': 'high_download'
                },
                'epic_games': {
                    'domains': ['epicgames.com'],
                    'sni_patterns': [r'.*\.epicgames\.com'],
                    'ports': [443],
                    'traffic_pattern': 'high_download'
                },
                'xbox_live': {
                    'domains': ['xboxlive.com', 'xbox.com'],
                    'sni_patterns': [r'.*\.xboxlive\.com'],
                    'ports': [3074],
                    'traffic_pattern': 'bidirectional'
                }
            },
            'cloud_storage': {
                'dropbox': {
                    'domains': ['dropbox.com', 'dropboxusercontent.com'],
                    'sni_patterns': [r'.*\.dropbox\.com'],
                    'ports': [443],
                    'traffic_pattern': 'bidirectional'
                },
                'google_drive': {
                    'domains': ['drive.google.com', 'docs.google.com'],
                    'sni_patterns': [r'.*\.drive\.google\.com'],
                    'ports': [443],
                    'traffic_pattern': 'bidirectional'
                },
                'onedrive': {
                    'domains': ['onedrive.live.com', '1drv.com'],
                    'sni_patterns': [r'.*\.onedrive\.live\.com'],
                    'ports': [443],
                    'traffic_pattern': 'bidirectional'
                }
            }
        }
    
    async def start_capture(self, interface: str = None, duration: int = 60):
        """
        Start packet capture and analysis
        """
        
        logger.info(f"Starting DPI capture on interface {interface or 'default'} for {duration}s")
        
        self.is_capturing = True
        
        # Start packet sniffing in background
        capture_task = asyncio.create_task(
            self._capture_packets(interface, duration)
        )
        
        return capture_task
    
    async def _capture_packets(self, interface: Optional[str], duration: int):
        """Capture and analyze packets"""
        
        def packet_handler(packet):
            try:
                self._analyze_packet(packet)
            except Exception as e:
                logger.error(f"Error analyzing packet: {e}")
        
        # Run packet capture in thread pool
        await asyncio.to_thread(
            sniff,
            iface=interface,
            prn=packet_handler,
            timeout=duration,
            store=False
        )
        
        self.is_capturing = False
        logger.info("DPI capture completed")
    
    def _analyze_packet(self, packet):
        """Analyze individual packet"""
        
        if not packet.haslayer(IP):
            return
        
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        # DNS Analysis
        if packet.haslayer(DNS):
            self._analyze_dns(packet, src_ip, dst_ip)
        
        # HTTP Analysis
        if packet.haslayer(HTTPRequest):
            self._analyze_http(packet, src_ip, dst_ip)
        
        # TLS/HTTPS Analysis (SNI extraction)
        if packet.haslayer(TLS):
            self._analyze_tls(packet, src_ip, dst_ip)
        
        # TCP/UDP Traffic Statistics
        if packet.haslayer(TCP) or packet.haslayer(UDP):
            self._update_traffic_stats(packet, src_ip, dst_ip)
    
    def _analyze_dns(self, packet, src_ip: str, dst_ip: str):
        """Analyze DNS queries and responses"""
        
        dns_layer = packet[DNS]
        
        # DNS Query
        if dns_layer.qr == 0 and packet.haslayer(DNSQR):
            query = packet[DNSQR].qname.decode('utf-8').rstrip('.')
            
            logger.debug(f"DNS Query: {src_ip} -> {query}")
            
            # Store DNS query
            if src_ip not in self.dns_cache:
                self.dns_cache[src_ip] = []
            
            self.dns_cache[src_ip].append({
                'query': query,
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'query'
            })
            
            # Check for application signatures
            app = self._identify_application_from_domain(query)
            if app:
                self.traffic_patterns[src_ip]['applications'].add(app)
        
        # DNS Response
        elif dns_layer.qr == 1 and packet.haslayer(DNSRR):
            for i in range(dns_layer.ancount):
                answer = packet[DNSRR][i]
                if answer.type == 1:  # A record
                    domain = answer.rrname.decode('utf-8').rstrip('.')
                    ip = answer.rdata
                    
                    logger.debug(f"DNS Response: {domain} -> {ip}")
                    
                    # Map IP to domain
                    if dst_ip not in self.dns_cache:
                        self.dns_cache[dst_ip] = []
                    
                    self.dns_cache[dst_ip].append({
                        'domain': domain,
                        'ip': ip,
                        'timestamp': datetime.utcnow().isoformat(),
                        'type': 'response'
                    })
    
    def _analyze_http(self, packet, src_ip: str, dst_ip: str):
        """Analyze HTTP requests"""
        
        http_layer = packet[HTTPRequest]
        
        host = http_layer.Host.decode('utf-8') if http_layer.Host else 'unknown'
        path = http_layer.Path.decode('utf-8') if http_layer.Path else '/'
        method = http_layer.Method.decode('utf-8') if http_layer.Method else 'GET'
        
        logger.debug(f"HTTP {method}: {src_ip} -> {host}{path}")
        
        # Identify application
        app = self._identify_application_from_domain(host)
        if app:
            self.traffic_patterns[src_ip]['applications'].add(app)
        
        self.traffic_patterns[src_ip]['protocols'].add('HTTP')
    
    def _analyze_tls(self, packet, src_ip: str, dst_ip: str):
        """Analyze TLS/HTTPS traffic and extract SNI"""
        
        try:
            tls_layer = packet[TLS]
            
            # Try to extract SNI (Server Name Indication)
            if hasattr(tls_layer, 'msg') and tls_layer.msg:
                for msg in tls_layer.msg:
                    if hasattr(msg, 'ext') and msg.ext:
                        for ext in msg.ext:
                            if hasattr(ext, 'servernames') and ext.servernames:
                                for servername in ext.servernames:
                                    if hasattr(servername, 'servername'):
                                        sni = servername.servername.decode('utf-8')
                                        
                                        logger.debug(f"TLS SNI: {src_ip} -> {sni}")
                                        
                                        # Identify application from SNI
                                        app = self._identify_application_from_sni(sni)
                                        if app:
                                            self.traffic_patterns[src_ip]['applications'].add(app)
            
            self.traffic_patterns[src_ip]['protocols'].add('TLS')
        
        except Exception as e:
            logger.debug(f"Error parsing TLS: {e}")
    
    def _update_traffic_stats(self, packet, src_ip: str, dst_ip: str):
        """Update traffic statistics"""
        
        packet_size = len(packet)
        
        # Update sent bytes
        self.traffic_patterns[src_ip]['bytes_sent'] += packet_size
        
        # Update received bytes
        self.traffic_patterns[dst_ip]['bytes_received'] += packet_size
        
        # Track connection
        if packet.haslayer(TCP):
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            
            connection = {
                'src_ip': src_ip,
                'src_port': src_port,
                'dst_ip': dst_ip,
                'dst_port': dst_port,
                'protocol': 'TCP',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.traffic_patterns[src_ip]['connections'].append(connection)
    
    def _identify_application_from_domain(self, domain: str) -> Optional[str]:
        """Identify application from domain name"""
        
        domain_lower = domain.lower()
        
        for category, apps in self.application_signatures.items():
            for app_name, app_data in apps.items():
                for app_domain in app_data['domains']:
                    if app_domain in domain_lower:
                        return f"{category}/{app_name}"
        
        return None
    
    def _identify_application_from_sni(self, sni: str) -> Optional[str]:
        """Identify application from SNI"""
        
        sni_lower = sni.lower()
        
        for category, apps in self.application_signatures.items():
            for app_name, app_data in apps.items():
                for pattern in app_data.get('sni_patterns', []):
                    if re.match(pattern, sni_lower):
                        return f"{category}/{app_name}"
        
        return None
    
    def get_device_applications(self, ip_address: str) -> Dict[str, any]:
        """Get applications used by a device"""
        
        if ip_address not in self.traffic_patterns:
            return {
                'ip_address': ip_address,
                'applications': [],
                'bandwidth': {'sent': 0, 'received': 0},
                'protocols': []
            }
        
        pattern = self.traffic_patterns[ip_address]
        
        # Group applications by category
        apps_by_category = defaultdict(list)
        for app in pattern['applications']:
            category, app_name = app.split('/')
            apps_by_category[category].append(app_name)
        
        return {
            'ip_address': ip_address,
            'applications': dict(apps_by_category),
            'bandwidth': {
                'sent_mb': round(pattern['bytes_sent'] / 1_000_000, 2),
                'received_mb': round(pattern['bytes_received'] / 1_000_000, 2),
                'total_mb': round((pattern['bytes_sent'] + pattern['bytes_received']) / 1_000_000, 2)
            },
            'protocols': list(pattern['protocols']),
            'connection_count': len(pattern['connections'])
        }
    
    def get_dns_history(self, ip_address: str) -> List[Dict]:
        """Get DNS query history for device"""
        
        return self.dns_cache.get(ip_address, [])
    
    def get_network_summary(self) -> Dict[str, any]:
        """Get network-wide DPI summary"""
        
        total_devices = len(self.traffic_patterns)
        total_bandwidth = sum(
            p['bytes_sent'] + p['bytes_received']
            for p in self.traffic_patterns.values()
        )
        
        # Count applications
        all_apps = set()
        for pattern in self.traffic_patterns.values():
            all_apps.update(pattern['applications'])
        
        # Top applications by bandwidth
        app_bandwidth = defaultdict(int)
        for ip, pattern in self.traffic_patterns.items():
            for app in pattern['applications']:
                app_bandwidth[app] += pattern['bytes_sent'] + pattern['bytes_received']
        
        top_apps = sorted(
            app_bandwidth.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_devices': total_devices,
            'total_bandwidth_mb': round(total_bandwidth / 1_000_000, 2),
            'unique_applications': len(all_apps),
            'top_applications': [
                {
                    'name': app,
                    'bandwidth_mb': round(bandwidth / 1_000_000, 2)
                }
                for app, bandwidth in top_apps
            ],
            'is_capturing': self.is_capturing
        }
