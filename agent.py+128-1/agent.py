#!/usr/bin/env python3
"""
NetScan Network Agent
Lightweight remote network scanner
"""
import asyncio
import aiohttp
import platform
import psutil
import json
import time
import os
from scapy.all import ARP, Ether, srp, conf

# Disable verbose output
conf.verb = 0

class NetScanAgent:
    def __init__(self, api_url, agent_key):
        self.api_url = api_url
        self.agent_key = agent_key
        self.session = None
        self.agent_id = platform.node()
    
    async def scan_network(self, network="192.168.1.0/24"):
        """Quick ARP scan of local network"""
        try:
            arp = ARP(pdst=network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            result = srp(packet, timeout=3, verbose=0)[0]
            devices = []
            
            for sent, received in result:
                devices.append({
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'timestamp': time.time()
                })
            
            return devices
        except Exception as e:
            print(f"Scan error: {e}")
            return []
    
    async def get_system_info(self):
        """Get agent system information"""
        return {
            'agent_id': self.agent_id,
            'hostname': platform.node(),
            'platform': platform.system(),
            'platform_version': platform.version(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_interfaces': list(psutil.net_if_addrs().keys()),
            'uptime': time.time() - psutil.boot_time()
        }
    
    async def get_network_stats(self):
        """Get network statistics"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errors_in': net_io.errin,
            'errors_out': net_io.errout
        }
    
    async def report_to_server(self, data):
        """Send data to server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/agent/report",
                    json=data,
                    headers={
                        'X-Agent-Key': self.agent_key,
                        'Content-Type': 'application/json'
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        print(f"Server error: {resp.status}")
                        return None
        except Exception as e:
            print(f"Report error: {e}")
            return None
    
    async def run(self):
        """Main agent loop"""
        print(f"🚀 NetScan Agent v2.0 Started")
        print(f"📡 Agent ID: {self.agent_id}")
        print(f"🌐 API: {self.api_url}")
        print(f"⏱️  Scan interval: 60 seconds")
        print("-" * 50)
        
        scan_count = 0
        
        while True:
            try:
                scan_count += 1
                print(f"\n🔍 Scan #{scan_count} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Get system info
                system_info = await self.get_system_info()
                print(f"💻 CPU: {system_info['cpu_percent']:.1f}% | RAM: {system_info['memory_percent']:.1f}%")
                
                # Get network stats
                network_stats = await self.get_network_stats()
                
                # Scan local network
                print("🔎 Scanning network...")
                devices = await self.scan_network()
                print(f"✅ Found {len(devices)} device(s)")
                
                # Report to server
                report = {
                    'agent': system_info,
                    'network_stats': network_stats,
                    'devices': devices,
                    'scan_timestamp': time.time(),
                    'scan_count': scan_count
                }
                
                print("📤 Reporting to server...")
                result = await self.report_to_server(report)
                
                if result:
                    print(f"✅ Report sent successfully")
                else:
                    print(f"⚠️  Report failed")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Agent stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Wait 60 seconds
            print(f"⏳ Next scan in 60 seconds...")
            await asyncio.sleep(60)

def main():
    # Get configuration from environment
    api_url = os.getenv('NETSCAN_API_URL', 'https://netscan-production.up.railway.app')
    agent_key = os.getenv('NETSCAN_AGENT_KEY')
    
    if not agent_key:
        print("❌ Error: NETSCAN_AGENT_KEY environment variable not set")
        print("Usage: NETSCAN_AGENT_KEY=your-key python agent.py")
        return
    
    # Create and run agent
    agent = NetScanAgent(api_url, agent_key)
    
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
