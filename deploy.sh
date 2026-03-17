#!/bin/bash

# NetScan v2.0 - Quick Deployment Script
# This script automates the deployment process

set -e

echo "🚀 NetScan v2.0 - Deployment Script"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    
    # Generate secure secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/change-this-secret-key-to-something-very-secure-minimum-32-characters/$SECRET_KEY/" .env
    
    # Generate secure database password
    DB_PASSWORD=$(openssl rand -hex 16)
    sed -i "s/change_this_password/$DB_PASSWORD/g" .env
    
    echo "✅ .env file created with secure credentials"
    echo ""
    echo "⚠️  IMPORTANT: Review and update .env file with your settings!"
    echo "Press Enter to continue or Ctrl+C to abort..."
    read
else
    echo "✅ .env file found"
fi

echo ""
echo "🏗️  Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🎉 NetScan v2.0 is now deployed!"
    echo ""
    echo "📍 Access URLs:"
    echo "   Frontend:  http://localhost:5173"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📊 Check logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose down"
    echo ""
    echo "🔄 Restart services:"
    echo "   docker-compose restart"
    echo ""
else
    echo "❌ Some services failed to start. Check logs:"
    echo "   docker-compose logs"
    exit 1
fi
