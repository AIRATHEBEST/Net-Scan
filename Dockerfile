FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent
COPY agent.py .

# Make executable
RUN chmod +x agent.py

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Run as root for network access
USER root

# Start agent
CMD ["python", "-u", "agent.py"]
