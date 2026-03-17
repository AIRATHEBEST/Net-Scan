import asyncio
import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import os
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class DeviceIntelligenceEngine:
    """
    🔥 Tier 1 Feature #1: Device Intelligence Engine
    
    Enhanced device fingerprinting with:
    - Comprehensive fingerprint database
    - Port + service → device class mapping
    - Detailed device identification
    - ML-ready classification
    
    Goal: "iPhone 13 running iOS 17" not just "Apple device"
    """
    
    def __init__(self):
        self.fingerprint_db = self._load_fingerprint_database()
        self.device_signatures = self._load_device_signatures()
    
    def _load_fingerprint_database(self) -> Dict:
        """Load comprehensive device fingerprint database"""
        return {
            # Apple Devices
            'apple': {
                'iphone': {
                    'models': {
                        'iPhone15,2': 'iPhone 14 Pro',
                        'iPhone15,3': 'iPhone 14 Pro Max',
                        'iPhone14,2': 'iPhone 13 Pro',
                        'iPhone14,3': 'iPhone 13 Pro Max',
                        'iPhone13,2': 'iPhone 12',
                        'iPhone13,3': 'iPhone 12 Pro',
                    },
                    'ports': [62078, 5353],  # Apple services
                    'services': ['_airplay', '_homekit', '_apple-mobdev2'],
                    'user_agents': ['iPhone', 'iOS'],
                },
                'ipad': {
                    'models': {
                        'iPad13,18': 'iPad Pro 12.9" (6th gen)',
                        'iPad13,16': 'iPad Pro 11" (4th gen)',
                    },
                    'ports': [62078, 5353],
                    'services': ['_airplay', '_homekit'],
                },
                'macbook': {
                    'models': {
                        'MacBookPro18,1': 'MacBook Pro 16" (2021)',
                        'MacBookPro18,3': 'MacBook Pro 14" (2021)',
                        'MacBookAir10,1': 'MacBook Air (M1)',
                    },
                    'ports': [22, 88, 445, 548, 5353],
                    'services': ['_smb', '_afpovertcp', '_ssh'],
                },
                'apple_tv': {
                    'ports': [3689, 7000, 49152],
                    'services': ['_airplay', '_raop'],
                },
                'homepod': {
                    'ports': [7000, 49152],
                    'services': ['_airplay', '_homekit'],
                }
            },
            
            # Samsung Devices
            'samsung': {
                'galaxy_phone': {
                    'models': {
                        'SM-S918': 'Galaxy S23 Ultra',
                        'SM-S916': 'Galaxy S23+',
                        'SM-S911': 'Galaxy S23',
                        'SM-S908': 'Galaxy S22 Ultra',
                    },
                    'services': ['_androidtvremote2'],
                    'dhcp_fingerprint': 'android',
                },
                'galaxy_tablet': {
                    'models': {
                        'SM-X900': 'Galaxy Tab S9 Ultra',
                        'SM-X800': 'Galaxy Tab S9',
                    }
                },
                'smart_tv': {
                    'ports': [8001, 8002, 9119],
                    'services': ['_samsung-remote'],
                }
            },
            
            # Google Devices
            'google': {
                'pixel': {
                    'models': {
                        'Pixel 8 Pro': 'Pixel 8 Pro',
                        'Pixel 8': 'Pixel 8',
                        'Pixel 7 Pro': 'Pixel 7 Pro',
                    },
                    'dhcp_fingerprint': 'android',
                },
                'nest': {
                    'hub': {
                        'ports': [8008, 8009],
                        'services': ['_googlecast'],
                    },
                    'camera': {
                        'ports': [443, 8883],
                        'services': ['_nest'],
                    },
                    'thermostat': {
                        'ports': [443],
                    }
                },
                'chromecast': {
                    'ports': [8008, 8009],
                    'services': ['_googlecast'],
                }
            },
            
            # Smart Home Devices
            'smart_home': {
                'philips_hue': {
                    'ports': [80, 443],
                    'services': ['_hue'],
                },
                'ring': {
                    'doorbell': {
                        'ports': [443, 8883],
                    },
                    'camera': {
                        'ports': [443, 8883],
                    }
                },
                'amazon_echo': {
                    'ports': [443, 4070],
                    'services': ['_amzn-alexa'],
                },
                'wyze': {
                    'camera': {
                        'ports': [554, 6668],
                    }
                }
            },
            
            # Gaming Consoles
            'gaming': {
                'playstation': {
                    'ps5': {
                        'ports': [9295, 9296, 9297],
                    },
                    'ps4': {
                        'ports': [9295],
                    }
                },
                'xbox': {
                    'series_x': {
                        'ports': [3074],
                    },
                    'one': {
                        'ports': [3074],
                    }
                },
                'nintendo_switch': {
                    'ports': [1024, 6667, 12400, 28910, 29900, 29901, 29920],
                }
            },
            
            # Computers
            'computers': {
                'windows': {
                    'ports': [135, 139, 445, 3389],
                    'services': ['_smb', '_rdp'],
                },
                'linux': {
                    'ports': [22, 111, 2049],
                    'services': ['_ssh', '_nfs'],
                }
            },
            
            # Network Equipment
            'network': {
                'router': {
                    'ports': [53, 80, 443, 8080],
                    'services': ['_http', '_https'],
                },
                'nas': {
                    'synology': {
                        'ports': [5000, 5001],
                    },
                    'qnap': {
                        'ports': [8080, 443],
                    }
                }
            }
        }
    
    def _load_device_signatures(self) -> Dict:
        """Load device-specific signatures for accurate identification"""
        return {
            'os_signatures': {
                'iOS 17': {
                    'ttl': 64,
                    'window_size': 65535,
                    'user_agent_pattern': r'iPhone.*OS 17',
                },
                'iOS 16': {
                    'ttl': 64,
                    'window_size': 65535,
                    'user_agent_pattern': r'iPhone.*OS 16',
                },
                'Android 14': {
                    'ttl': 64,
                    'user_agent_pattern': r'Android 14',
                },
                'Windows 11': {
                    'ttl': 128,
                    'window_size': 65535,
                },
                'macOS Sonoma': {
                    'ttl': 64,
                    'user_agent_pattern': r'Mac OS X 14',
                }
            },
            'service_signatures': {
                'airplay': {'port': 7000, 'vendor': 'Apple'},
                'homekit': {'port': 5353, 'vendor': 'Apple'},
                'chromecast': {'port': 8009, 'vendor': 'Google'},
                'alexa': {'port': 4070, 'vendor': 'Amazon'},
            }
        }
    
    async def identify_device_detailed(
        self,
        mac: str,
        ip: str,
        vendor: str,
        hostname: Optional[str],
        open_ports: List[int],
        services: Dict,
        os_info: Optional[Dict],
        dhcp_fingerprint: Optional[str],
        user_agent: Optional[str],
        mdns_services: Optional[Dict]
    ) -> Dict[str, any]:
        """
        Perform detailed device identification
        Returns specific model and OS version
        """
        
        identification = {
            'device_type': 'unknown',
            'manufacturer': vendor,
            'model': None,
            'os': None,
            'os_version': None,
            'confidence': 0,
            'details': {}
        }
        
        # Apple Device Detection
        if 'apple' in vendor.lower():
            apple_result = self._identify_apple_device(
                hostname, open_ports, services, user_agent, mdns_services
            )
            if apple_result:
                identification.update(apple_result)
                identification['confidence'] = 95
                return identification
        
        # Samsung Device Detection
        if 'samsung' in vendor.lower():
            samsung_result = self._identify_samsung_device(
                hostname, open_ports, dhcp_fingerprint
            )
            if samsung_result:
                identification.update(samsung_result)
                identification['confidence'] = 90
                return identification
        
        # Google Device Detection
        if 'google' in vendor.lower():
            google_result = self._identify_google_device(
                hostname, open_ports, services
            )
            if google_result:
                identification.update(google_result)
                identification['confidence'] = 90
                return identification
        
        # Smart Home Device Detection
        smart_home_result = self._identify_smart_home_device(
            vendor, hostname, open_ports, services
        )
        if smart_home_result:
            identification.update(smart_home_result)
            identification['confidence'] = 85
            return identification
        
        # Gaming Console Detection
        gaming_result = self._identify_gaming_console(
            vendor, hostname, open_ports
        )
        if gaming_result:
            identification.update(gaming_result)
            identification['confidence'] = 90
            return identification
        
        # Computer Detection
        computer_result = self._identify_computer(
            vendor, hostname, open_ports, os_info
        )
        if computer_result:
            identification.update(computer_result)
            identification['confidence'] = 80
            return identification
        
        # Fallback to basic classification
        return identification
    
    def _identify_apple_device(
        self,
        hostname: Optional[str],
        open_ports: List[int],
        services: Dict,
        user_agent: Optional[str],
        mdns_services: Optional[Dict]
    ) -> Optional[Dict]:
        """Identify specific Apple device model and iOS version"""
        
        result = {
            'manufacturer': 'Apple',
            'details': {}
        }
        
        # Check for iPhone
        if user_agent and 'iphone' in user_agent.lower():
            result['device_type'] = 'smartphone'
            
            # Extract iOS version
            ios_match = re.search(r'OS (\d+)_(\d+)', user_agent)
            if ios_match:
                result['os'] = 'iOS'
                result['os_version'] = f"{ios_match.group(1)}.{ios_match.group(2)}"
            
            # Try to identify model
            model_match = re.search(r'iPhone(\d+),(\d+)', user_agent)
            if model_match:
                model_id = f"iPhone{model_match.group(1)},{model_match.group(2)}"
                if model_id in self.fingerprint_db['apple']['iphone']['models']:
                    result['model'] = self.fingerprint_db['apple']['iphone']['models'][model_id]
            
            if not result.get('model'):
                result['model'] = 'iPhone (Unknown Model)'
            
            return result
        
        # Check for iPad
        if user_agent and 'ipad' in user_agent.lower():
            result['device_type'] = 'tablet'
            result['model'] = 'iPad'
            result['os'] = 'iPadOS'
            return result
        
        # Check for Mac
        if hostname and any(x in hostname.lower() for x in ['macbook', 'imac', 'mac-mini']):
            result['device_type'] = 'laptop' if 'macbook' in hostname.lower() else 'desktop'
            result['model'] = hostname.replace('.local', '')
            result['os'] = 'macOS'
            
            # Check for macOS version
            if 548 in open_ports:  # AFP
                result['details']['file_sharing'] = True
            
            return result
        
        # Check for Apple TV
        if mdns_services and '_airplay._tcp' in str(mdns_services):
            if 7000 in open_ports:
                result['device_type'] = 'tv'
                result['model'] = 'Apple TV'
                result['os'] = 'tvOS'
                return result
        
        # Check for HomePod
        if mdns_services and '_homekit._tcp' in str(mdns_services):
            if 7000 in open_ports and hostname and 'homepod' in hostname.lower():
                result['device_type'] = 'iot'
                result['model'] = 'HomePod'
                result['os'] = 'audioOS'
                return result
        
        return None
    
    def _identify_samsung_device(
        self,
        hostname: Optional[str],
        open_ports: List[int],
        dhcp_fingerprint: Optional[str]
    ) -> Optional[Dict]:
        """Identify Samsung device"""
        
        result = {
            'manufacturer': 'Samsung',
            'details': {}
        }
        
        # Check for Galaxy phone
        if dhcp_fingerprint and 'android' in dhcp_fingerprint.lower():
            if hostname and 'galaxy' in hostname.lower():
                result['device_type'] = 'smartphone'
                result['model'] = hostname.replace('-', ' ').title()
                result['os'] = 'Android'
                return result
        
        # Check for Samsung TV
        if 8001 in open_ports or 8002 in open_ports:
            result['device_type'] = 'tv'
            result['model'] = 'Samsung Smart TV'
            result['os'] = 'Tizen'
            return result
        
        return None
    
    def _identify_google_device(
        self,
        hostname: Optional[str],
        open_ports: List[int],
        services: Dict
    ) -> Optional[Dict]:
        """Identify Google device"""
        
        result = {
            'manufacturer': 'Google',
            'details': {}
        }
        
        # Check for Chromecast
        if 8008 in open_ports and 8009 in open_ports:
            result['device_type'] = 'tv'
            result['model'] = 'Chromecast'
            result['os'] = 'Google Cast'
            return result
        
        # Check for Nest devices
        if hostname and 'nest' in hostname.lower():
            if 'camera' in hostname.lower():
                result['device_type'] = 'camera'
                result['model'] = 'Nest Camera'
            elif 'hub' in hostname.lower():
                result['device_type'] = 'iot'
                result['model'] = 'Google Nest Hub'
            elif 'thermostat' in hostname.lower():
                result['device_type'] = 'iot'
                result['model'] = 'Nest Thermostat'
            else:
                result['device_type'] = 'iot'
                result['model'] = 'Nest Device'
            return result
        
        return None
    
    def _identify_smart_home_device(
        self,
        vendor: str,
        hostname: Optional[str],
        open_ports: List[int],
        services: Dict
    ) -> Optional[Dict]:
        """Identify smart home devices"""
        
        # Ring devices
        if 'ring' in vendor.lower() or (hostname and 'ring' in hostname.lower()):
            result = {
                'manufacturer': 'Ring',
                'device_type': 'camera',
                'os': 'Ring OS'
            }
            if hostname and 'doorbell' in hostname.lower():
                result['model'] = 'Ring Video Doorbell'
            else:
                result['model'] = 'Ring Camera'
            return result
        
        # Philips Hue
        if 'philips' in vendor.lower() and (hostname and 'hue' in hostname.lower()):
            return {
                'manufacturer': 'Philips',
                'device_type': 'iot',
                'model': 'Hue Bridge',
                'details': {'type': 'smart_lighting'}
            }
        
        # Amazon Echo
        if 'amazon' in vendor.lower() and 4070 in open_ports:
            return {
                'manufacturer': 'Amazon',
                'device_type': 'iot',
                'model': 'Echo Device',
                'os': 'Fire OS'
            }
        
        # Wyze Camera
        if 'wyze' in vendor.lower() or (hostname and 'wyze' in hostname.lower()):
            return {
                'manufacturer': 'Wyze',
                'device_type': 'camera',
                'model': 'Wyze Cam'
            }
        
        return None
    
    def _identify_gaming_console(
        self,
        vendor: str,
        hostname: Optional[str],
        open_ports: List[int]
    ) -> Optional[Dict]:
        """Identify gaming consoles"""
        
        # PlayStation
        if 'sony' in vendor.lower() and 9295 in open_ports:
            result = {
                'manufacturer': 'Sony',
                'device_type': 'gaming'
            }
            if 9296 in open_ports and 9297 in open_ports:
                result['model'] = 'PlayStation 5'
            else:
                result['model'] = 'PlayStation 4'
            return result
        
        # Xbox
        if 'microsoft' in vendor.lower() and 3074 in open_ports:
            return {
                'manufacturer': 'Microsoft',
                'device_type': 'gaming',
                'model': 'Xbox Console'
            }
        
        # Nintendo Switch
        if 'nintendo' in vendor.lower() or (hostname and 'switch' in hostname.lower()):
            return {
                'manufacturer': 'Nintendo',
                'device_type': 'gaming',
                'model': 'Nintendo Switch'
            }
        
        return None
    
    def _identify_computer(
        self,
        vendor: str,
        hostname: Optional[str],
        open_ports: List[int],
        os_info: Optional[Dict]
    ) -> Optional[Dict]:
        """Identify computers"""
        
        result = {
            'manufacturer': vendor,
            'details': {}
        }
        
        # Windows PC
        if 445 in open_ports or 3389 in open_ports:
            result['device_type'] = 'desktop'
            result['os'] = 'Windows'
            
            if os_info:
                result['os_version'] = os_info.get('name', 'Unknown Version')
            
            if hostname:
                result['model'] = hostname
            else:
                result['model'] = 'Windows PC'
            
            return result
        
        # Linux
        if 22 in open_ports and os_info and 'linux' in os_info.get('name', '').lower():
            result['device_type'] = 'desktop'
            result['os'] = 'Linux'
            result['os_version'] = os_info.get('name', 'Unknown Distribution')
            result['model'] = hostname or 'Linux Computer'
            return result
        
        return None
    
    async def extract_device_capabilities(
        self,
        device_info: Dict
    ) -> List[str]:
        """Extract device capabilities for better UX"""
        
        capabilities = []
        
        device_type = device_info.get('device_type')
        open_ports = device_info.get('open_ports', [])
        services = device_info.get('services', {})
        
        # Media capabilities
        if device_type in ['tv', 'gaming']:
            capabilities.append('media_streaming')
        
        # File sharing
        if 445 in open_ports or 548 in open_ports:
            capabilities.append('file_sharing')
        
        # Remote access
        if 22 in open_ports or 3389 in open_ports:
            capabilities.append('remote_access')
        
        # Smart home control
        if device_type == 'iot':
            capabilities.append('smart_home')
        
        # Camera/Security
        if device_type == 'camera':
            capabilities.append('security')
        
        return capabilities
