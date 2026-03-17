FROM python:3.11-slim

LABEL maintainer="NetScan <support@netscan.com>"
LABEL description="NetScan Network Agent — lightweight remote scanner"

# System dependencies for Scapy / packet capture
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpcap-dev \
    tcpdump \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .
RUN chmod +x agent.py

# Health check: just verify Python can import the agent
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import agent" || exit 1

# Needs root for raw-socket / ARP scanning
USER root

ENV NETSCAN_API_URL=https://netscan-api-production.up.railway.app
ENV NETSCAN_AGENT_KEY=""

CMD ["python", "-u", "agent.py"]
