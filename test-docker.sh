#!/bin/bash

# Build and test script for Multi-service Dockerfile

echo "🐳 Building MCP Oxii + Temp API Docker image..."

# Build the simple version
echo "📦 Building simple version (2 separate ports)..."
docker build -f Dockerfile.simple -t mcp-oxii-simple:latest .

if [ $? -eq 0 ]; then
    echo "✅ Simple build successful!"
    
    echo "🧪 Testing simple container..."
    docker run -d --name mcp-test-simple -p 9031:9031 -p 8000:8000 mcp-oxii-simple:latest
    
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    echo "🔍 Testing health endpoints..."
    curl -f http://localhost:9031/health && echo " ✅ MCP Server healthy"
    curl -f http://localhost:8000/health && echo " ✅ Temp API healthy"
    
    echo "📊 Container logs:"
    docker logs mcp-test-simple --tail=20
    
    echo "🛑 Stopping test container..."
    docker stop mcp-test-simple && docker rm mcp-test-simple
    
else
    echo "❌ Simple build failed!"
    exit 1
fi

# Build the nginx proxy version
echo "📦 Building nginx proxy version (single port 80)..."
docker build -f Dockerfile -t mcp-oxii-proxy:latest .

if [ $? -eq 0 ]; then
    echo "✅ Proxy build successful!"
    
    echo "🧪 Testing proxy container..."
    docker run -d --name mcp-test-proxy -p 80:80 mcp-oxii-proxy:latest
    
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    echo "🔍 Testing endpoints..."
    curl -f http://localhost/health && echo " ✅ Health endpoint working"
    curl -f http://localhost/api/v1/plans && echo " ✅ Temp API accessible"
    
    echo "📊 Container logs:"
    docker logs mcp-test-proxy --tail=20
    
    echo "🛑 Stopping test container..."
    docker stop mcp-test-proxy && docker rm mcp-test-proxy
    
else
    echo "❌ Proxy build failed!"
    exit 1
fi

echo "🎉 All builds completed successfully!"
echo ""
echo "📋 Usage:"
echo "  Simple version (2 ports): docker run -p 9031:9031 -p 8000:8000 mcp-oxii-simple:latest"
echo "  Proxy version (1 port):   docker run -p 80:80 mcp-oxii-proxy:latest"
echo ""
echo "🔗 Endpoints:"
echo "  Simple version:"
echo "    - MCP Server: http://localhost:9031"
echo "    - Temp API: http://localhost:8000"
echo "  Proxy version:"
echo "    - Combined: http://localhost/"
echo "    - Health: http://localhost/health"
echo "    - API: http://localhost/api/v1/plans"