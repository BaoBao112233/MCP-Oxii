#!/bin/bash

# MCP-Oxii Deployment Script
echo "🚀 Starting MCP-Oxii Deployment..."

# Check if .env file exists
if [ ! -f "mcp/oxii-server/.env" ]; then
    echo "⚠️  Environment file not found!"
    echo "📋 Creating .env file from template..."
    cp mcp/oxii-server/.env.example mcp/oxii-server/.env
    echo "✅ Please edit mcp/oxii-server/.env with your credentials"
    echo "📝 Required variables:"
    echo "   - OXII_PHONE: Your phone number"
    echo "   - OXII_PASSWORD: Your password"
    echo "   - OXII_COUNTRY: Your country code (default: VI)"
    echo ""
    echo "🔧 After editing, run this script again to deploy"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🐳 Building and starting services..."

# Use simple compose file by default, prod file for advanced features
COMPOSE_FILE="docker-compose.simple.yml"
if [ "$1" = "--prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "🏭 Using production configuration with health checks"
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker compose -f $COMPOSE_FILE down

# Build and start services
echo "🔨 Building services..."
docker compose -f $COMPOSE_FILE build

echo "▶️  Starting services..."
docker compose -f $COMPOSE_FILE up -d

# Wait a moment for services to start
sleep 5

# Check service status
echo "📊 Service Status:"
docker compose -f $COMPOSE_FILE ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Service URLs:"
echo "   • MCP Oxii-Server: http://localhost:9031"
echo "   • Temp API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Check health:"
echo "   curl http://localhost:9031/health"
echo "   curl http://localhost:8000/health"
echo ""
echo "📋 Management commands:"
echo "   • View logs: docker compose -f $COMPOSE_FILE logs -f"
echo "   • Stop services: docker compose -f $COMPOSE_FILE down"
echo "   • Restart: ./deploy.sh"
echo ""