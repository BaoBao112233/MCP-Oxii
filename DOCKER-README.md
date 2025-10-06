# template Docker Compose Setup

This document provides instructions for running the template blockchain analysis platform using Docker Compose.

## Prerequisites

- Docker Engine installed (version 19.03.0+)
- Docker Compose installed (version 1.27.0+)
- Git (for cloning the repository)

## Setup Instructions

1. **Clone the Repository**

```bash
git clone <repository-url>
cd template
```

2. **Configure Environment Variables**

Copy the template environment file:

```bash
cp .env.template .env
```

Edit the `.env` file to set your API keys and other configuration parameters:

```
API_VERSION=1.0.0
APP_NAME=template
OPENAI_API_KEY=your_openai_api_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
DEBUG_MODE=true
BLOCKCHAIN_KNOWLEDGE_MCP_SERVER_URL=http://blockchain-knowledge:9091
ONCHAIN_INSIGHT_MCP_SERVER_URL=http://onchain-insight:9092
SOCIAL_INSIGHT_MCP_SERVER_URL=http://social-insight:9093
```

Note: The MCP server URLs have been adjusted to use the Docker Compose service names.

3. **Build and Start the Services**

```bash
docker-compose up -d
```

This command will:
- Build the Docker images for the main application and all MCP servers
- Create and start containers for each service
- Set up the necessary network
- Mount volumes for persistent data storage

4. **Verify Services**

Check that all services are running:

```bash
docker-compose ps
```

Test the API health endpoint:

```bash
curl http://localhost:7000/health
```

You should receive a response like: `{"status":"healthy"}`

## Service Access

- Main Application API: http://localhost:7000
- API Documentation: http://localhost:7000/docs
- Blockchain Knowledge MCP Server: http://localhost:9091
- Onchain Insight MCP Server: http://localhost:9092
- Social Insight MCP Server: http://localhost:9093

## Managing the Services

- **Stop all services**:
```bash
docker-compose stop
```

- **Start all services**:
```bash
docker-compose start
```

- **Restart all services**:
```bash
docker-compose restart
```

- **Stop and remove containers, networks, and volumes**:
```bash
docker-compose down
```

- **View logs**:
```bash
docker-compose logs -f
```

To view logs for a specific service:
```bash
docker-compose logs -f app  # or blockchain-knowledge, onchain-insight, social-insight
```

## Troubleshooting

- **Service not starting**: Check the logs for the specific service
- **Network connectivity issues**: Ensure the Docker network is created correctly
- **API errors**: Verify that the environment variables are set correctly
- **Database persistence**: Check that the volumes are mounted correctly
- **Poetry installation errors**: If you encounter an error about `--no-dev` option not existing, this is fixed in the Dockerfiles by using `--only main` instead, which is compatible with newer Poetry versions
- **Poetry package errors**: If you see errors related to Poetry not finding packages, the `--no-root` flag has been added to prevent Poetry from trying to install the current directory as a package
- **Python version errors**: If you encounter errors related to Python version requirements, all pyproject.toml files have been updated to specify Python `>=3.7,<4.0` to match the requirements of dependencies like cachetools

## Development with Docker

For local development with Docker Compose:

1. Make changes to your code
2. Rebuild the affected service:
```bash
docker-compose build app  # or blockchain-knowledge, onchain-insight, social-insight
```
3. Restart the service:
```bash
docker-compose up -d --no-deps app  # or blockchain-knowledge, onchain-insight, social-insight
``` 