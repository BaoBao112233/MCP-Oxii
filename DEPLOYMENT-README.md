# MCP-Oxii Production Deployment

This Docker Compose file deploys the MCP Oxii-server and Temp API without the chatbot.

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BaoBao112233/MCP-Oxii.git
   cd MCP-Oxii
   ```

2. **Set up environment files:**
   ```bash
   # Copy environment template for MCP Oxii-server
   cp mcp/oxii-server/.env.example mcp/oxii-server/.env
   
   # Edit the .env file with your credentials
   nano mcp/oxii-server/.env
   ```

3. **Deploy the services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

## 📦 Services

### MCP Oxii-Server
- **Port:** 9031
- **Purpose:** Model Context Protocol server for OXII smart home device control
- **Health Check:** `http://localhost:9031/health`
- **Tools Available:**
  - Device authentication
  - Device list retrieval
  - Switch device control
  - Air conditioner control
  - One-touch control (all devices/by type)
  - Cronjob creation for devices
  - Room one-touch control

### Temp API (Planning API)
- **Port:** 8000
- **Purpose:** FastAPI service for plan and task management
- **Health Check:** `http://localhost:8000/health`
- **Endpoints:**
  - `GET /api/v1/plans` - List all plans
  - `POST /api/v1/plans` - Create a new plan
  - `GET /api/v1/plans/{plan_id}` - Get plan by ID
  - `PUT /api/v1/plans/{plan_id}` - Update plan
  - `DELETE /api/v1/plans/{plan_id}` - Delete plan
  - `PUT /api/v1/plans/{plan_id}/tasks/{task_id}/status` - Update task status

## 🔧 Environment Configuration

Create `mcp/oxii-server/.env` with the following variables:

```env
# OXII Authentication
USER_PHONE=your_phone_number
USER_PASSWORD=your_password
USER_COUNTRY=VN

# API Settings
DEBUG_MODE=false
```

## 🛠️ Management Commands

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Stop services
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# View logs for specific service
docker-compose -f docker-compose.prod.yml logs -f oxii-server
docker-compose -f docker-compose.prod.yml logs -f temp-api

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

## 🔍 Health Checks

Both services include health endpoints:

```bash
# Check MCP Oxii-server
curl http://localhost:9031/health

# Check Temp API
curl http://localhost:8000/health
```

## 🚀 Quick Deploy

Use the provided deployment script:

```bash
# Simple deployment
./deploy.sh

# Production deployment with health checks
./deploy.sh --prod
```

## 🌐 Network Architecture

- **Network:** `mcp-network` (bridge driver)
- **Inter-service communication:** Services can communicate using service names
- **External access:** Both services exposed on their respective ports

## 📊 Monitoring

View service status:
```bash
# All services
docker-compose -f docker-compose.prod.yml ps

# Resource usage
docker stats

# Service logs
docker-compose -f docker-compose.prod.yml logs --tail=100 -f
```

## 🔧 Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using the ports
   lsof -i :9031
   lsof -i :8000
   ```

2. **Environment variables not loading:**
   ```bash
   # Verify .env file exists and has correct format
   cat mcp/oxii-server/.env
   ```

3. **Build failures:**
   ```bash
   # Clean build
   docker-compose -f docker-compose.prod.yml build --no-cache
   ```

4. **Service not starting:**
   ```bash
   # Check logs for specific service
   docker-compose -f docker-compose.prod.yml logs oxii-server
   ```

## 🔄 Updates

To update the services:

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📋 Testing

Test the deployed services:

```bash
# Test MCP Oxii-server health
curl http://localhost:9031/health

# Test Temp API health
curl http://localhost:8000/health

# Test Temp API functionality
curl http://localhost:8000/api/v1/plans

# Create a test plan
curl -X POST http://localhost:8000/api/v1/plans \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Plan", "description": "Test plan description"}'
```

## 🔒 Security Notes

- Ensure your `.env` file contains secure credentials
- Do not commit `.env` files to version control
- Consider using Docker secrets for production deployments
- Configure firewalls appropriately for production use

## 📝 License

See the main repository LICENSE file for details.