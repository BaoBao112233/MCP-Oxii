# 🐳 Multi-Service Dockerfile

Dockerfile tổng hợp để deploy cả MCP Oxii-server và Temp API trong một container duy nhất.

## 📦 Files được tạo

### 🎯 **Main Dockerfiles:**
1. **`Dockerfile`** - Version với Nginx reverse proxy (port 80)
2. **`Dockerfile.simple`** - Version đơn giản với 2 ports riêng biệt (9031, 8000)

### 🔧 **Configuration Files:**
- `docker-configs/supervisord.conf` - Supervisor configuration
- `docker-configs/nginx.conf` - Nginx reverse proxy config  
- `docker-configs/start.sh` - Startup script
- `test-docker.sh` - Build và test script

## 🚀 **Cách sử dụng**

### **Option 1: Simple Version (Recommended)**
Chạy 2 services trên 2 ports riêng biệt:

```bash
# Build
docker build -f Dockerfile.simple -t mcp-oxii-simple .

# Run
docker run -d -p 9031:9031 -p 8000:8000 --name mcp-oxii mcp-oxii-simple

# Test
curl http://localhost:9031/health  # MCP Server
curl http://localhost:8000/health  # Temp API
curl http://localhost:8000/docs    # API Documentation
```

### **Option 2: Nginx Proxy Version**
Chạy cả 2 services qua 1 port duy nhất với nginx:

```bash
# Build
docker build -f Dockerfile -t mcp-oxii-proxy .

# Run  
docker run -d -p 80:80 --name mcp-oxii-proxy mcp-oxii-proxy

# Test
curl http://localhost/health           # Health check
curl http://localhost/api/v1/plans     # Temp API
curl http://localhost/sse              # MCP SSE endpoint
```

### **Option 3: Auto Test**
```bash
# Test both versions automatically
./test-docker.sh
```

## 🔗 **Service Endpoints**

### **Simple Version (Dockerfile.simple):**
| Service | Port | Endpoint | Purpose |
|---------|------|----------|---------|
| MCP Server | 9031 | `http://localhost:9031` | Smart home device control |
| Temp API | 8000 | `http://localhost:8000` | Plan management API |

### **Proxy Version (Dockerfile):**
| Path | Target | Purpose |
|------|--------|---------|
| `/health` | Nginx | Combined health check |
| `/api/*` | Temp API | Plan management endpoints |
| `/sse` | MCP Server | Server-Sent Events |
| `/messages` | MCP Server | MCP messages |
| `/` | Temp API | Default routing |

## 🔧 **Environment Variables**

### **MCP Oxii-Server:**
```env
OXII_BASE_URL=https://stg-oxii-api.smarthiz.vn
OXII_PHONE=your_phone_number
OXII_PASSWORD=your_password  
OXII_COUNTRY=VI
PORT=9031
DEBUG=false
```

### **Temp API:**
```env
PORT=8000
```

## 📊 **Monitoring**

### **Health Checks:**
```bash
# Simple version
curl http://localhost:9031/health
curl http://localhost:8000/health

# Proxy version  
curl http://localhost/health
```

### **Logs:**
```bash
# Container logs
docker logs mcp-oxii -f

# Individual service logs (simple version)
docker exec mcp-oxii tail -f /var/log/supervisor/mcp-server.out.log
docker exec mcp-oxii tail -f /var/log/supervisor/temp-api.out.log
```

### **Service Status:**
```bash
# Check running processes
docker exec mcp-oxii supervisorctl status
```

## 🛠️ **Development**

### **Local Build:**
```bash
# Simple version
docker build -f Dockerfile.simple -t mcp-oxii:dev .

# Proxy version
docker build -f Dockerfile -t mcp-oxii:prod .
```

### **Debug Mode:**
```bash
# Run with interactive shell
docker run -it -p 9031:9031 -p 8000:8000 mcp-oxii:dev /bin/bash

# Check service status
supervisorctl status
```

## 🔒 **Security Features**

- ✅ Non-root user execution where possible
- ✅ Minimal attack surface
- ✅ Health checks enabled
- ✅ Process supervision with automatic restart
- ✅ Proper log management

## 📈 **Production Deployment**

### **Docker Compose:**
```yaml
services:
  mcp-oxii:
    build:
      context: .
      dockerfile: Dockerfile.simple
    ports:
      - "9031:9031"
      - "8000:8000"  
    environment:
      - OXII_PHONE=${OXII_PHONE}
      - OXII_PASSWORD=${OXII_PASSWORD}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9031/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **Cloud Deployment:**
```bash
# Push to registry
docker tag mcp-oxii-simple:latest your-registry/mcp-oxii:latest
docker push your-registry/mcp-oxii:latest

# Deploy on cloud platform
# Update render.yaml or your platform config
```

## 🧪 **Testing**

### **API Tests:**
```bash
# Test MCP Server tools (Simple version)
curl http://localhost:9031/docs.json

# Test Temp API endpoints  
curl http://localhost:8000/api/v1/plans
curl -X POST http://localhost:8000/api/v1/plans \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Plan", "description": "Test"}'
```

### **Load Testing:**
```bash
# Install apache bench
sudo apt install apache2-utils

# Test endpoints
ab -n 100 -c 10 http://localhost:8000/health
ab -n 100 -c 10 http://localhost:9031/health
```

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Services not starting:**
   ```bash
   # Check supervisor logs
   docker logs container-name
   docker exec container-name supervisorctl status
   ```

2. **Port conflicts:**
   ```bash
   # Check what's using ports
   lsof -i :9031
   lsof -i :8000
   ```

3. **Build failures:**
   ```bash
   # Clean build
   docker build --no-cache -f Dockerfile.simple -t mcp-oxii .
   ```

4. **Memory issues:**
   ```bash
   # Run with memory limit
   docker run -m 512m -p 9031:9031 -p 8000:8000 mcp-oxii
   ```

## 📋 **File Structure**

```
/app/
├── mcp-server/          # MCP Oxii-server files
│   ├── main.py
│   ├── tools/
│   └── pyproject.toml
├── temp-api/            # Temp API files  
│   ├── main.py
│   ├── requirements.txt
│   └── routers/
└── configs/             # Configuration files
    ├── supervisord.conf
    ├── nginx.conf
    └── start.sh
```

## 🎯 **Recommendations**

- **Development:** Use `Dockerfile.simple` for easier debugging
- **Production:** Use `Dockerfile.simple` with proper monitoring
- **Cloud:** Use `Dockerfile.simple` for most cloud platforms
- **High Traffic:** Consider `Dockerfile` with nginx for load balancing

## 📞 **Support**

For issues or questions:
1. Check container logs: `docker logs container-name`
2. Verify health endpoints are responding
3. Check supervisor process status
4. Review configuration files