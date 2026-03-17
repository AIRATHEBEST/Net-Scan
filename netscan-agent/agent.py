#!/usr/bin/env python3
"""
NetScan Network Agent v2.0
Lightweight remote network scanner that reports to the NetScan backend API.

Usage:
    NETSCAN_API_URL=https://your-backend.railway.app \
    NETSCAN_AGENT_KEY=your-agent-key \
    python agent.py
"""

import asyncio
import aiohttp
import platform
import psutil
import json
import time
import os
import socket

try:
    from scapy.all import ARP, Ether, srp, conf
    conf.verb = 0
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("⚠️  Scapy not available — ARP scanning disabled")


class NetScanAgent:
    def __init__(self, api_url: str, agent_key: str):
        self.api_url = api_url.rstrip("/")
        self.agent_key = agent_key
        self.agent_id = platform.node()

    async def scan_network(self, network: str = "192.168.1.0/24") -> list:
        """ARP scan of the local network segment."""
        if not SCAPY_AVAILABLE:
            return []
        try:
            arp = ARP(pdst=network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            result = srp(packet, timeout=3, verbose=0)[0]
            devices = []
            for _, received in result:
                devices.append({
                    "ip": received.psrc,
                    "mac": received.hwsrc,
                    "hostname": self._resolve_hostname(received.psrc),
                })
            return devices
        except Exception as e:
            print(f"❌ ARP scan error: {e}")
            return []

    def _resolve_hostname(self, ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return ""

    async def get_system_info(self) -> dict:
        """Collect local system metrics."""
        return {
            "agent_id": self.agent_id,
            "platform": platform.system(),
            "platform_version": platform.version(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "uptime": time.time() - psutil.boot_time(),
        }

    async def get_network_stats(self) -> dict:
        """Collect network I/O statistics."""
        counters = psutil.net_io_counters()
        return {
            "bytes_sent": counters.bytes_sent,
            "bytes_recv": counters.bytes_recv,
            "packets_sent": counters.packets_sent,
            "packets_recv": counters.packets_recv,
        }

    async def report_to_server(self, data: dict) -> dict | None:
        """POST scan report to the NetScan backend API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/agent/report",
                    json=data,
                    headers={
                        "X-Agent-Key": self.agent_key,
                        "Content-Type": "application/json",
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        print(f"⚠️  Server responded {resp.status}")
                        return None
        except Exception as e:
            print(f"❌ Report error: {e}")
            return None

    async def run(self):
        """Main agent loop — scan every 60 seconds and report."""
        print(f"🚀 NetScan Agent v2.0 Started")
        print(f"📡 Agent ID : {self.agent_id}")
        print(f"🌐 API URL  : {self.api_url}")
        print(f"⏱️  Interval : 60 seconds")
        print("-" * 50)

        scan_count = 0
        while True:
            try:
                scan_count += 1
                print(f"\n🔍 Scan #{scan_count} — {time.strftime('%Y-%m-%d %H:%M:%S')}")

                system_info = await self.get_system_info()
                print(
                    f"💻 CPU: {system_info['cpu_percent']:.1f}%  "
                    f"RAM: {system_info['memory_percent']:.1f}%"
                )

                network_stats = await self.get_network_stats()

                print("🔎 Scanning network …")
                devices = await self.scan_network()
                print(f"✅ Found {len(devices)} device(s)")

                report = {
                    "agent": system_info,
                    "network_stats": network_stats,
                    "devices": devices,
                    "scan_timestamp": time.time(),
                    "scan_count": scan_count,
                }

                print("📤 Reporting to server …")
                result = await self.report_to_server(report)
                if result:
                    print("✅ Report accepted")
                else:
                    print("⚠️  Report not acknowledged")

            except KeyboardInterrupt:
                print("\n🛑 Agent stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

            print("⏳ Next scan in 60 seconds …")
            await asyncio.sleep(60)


def main():
    api_url = os.getenv("NETSCAN_API_URL", "https://netscan-api-production.up.railway.app")
    agent_key = os.getenv("NETSCAN_AGENT_KEY", "")

    if not agent_key:
        print("❌ NETSCAN_AGENT_KEY environment variable is not set.")
        print("   Usage: NETSCAN_AGENT_KEY=your-key python agent.py")
        return

    agent = NetScanAgent(api_url, agent_key)
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
