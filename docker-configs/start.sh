#!/bin/bash

# Start script for MCP Oxii + Temp API services
echo "🚀 Starting MCP Oxii + Temp API services..."

# Copy configuration files
echo "📝 Setting up configurations..."
cp /app/configs/supervisord.conf /etc/supervisor/conf.d/
cp /app/configs/nginx.conf /etc/nginx/

# Create log directories
mkdir -p /var/log/supervisor
mkdir -p /var/log/nginx

# Wait a moment for file system
sleep 2

echo "✅ Configuration complete. Starting services..."

# Start supervisor to manage both services + nginx
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf