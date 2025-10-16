# Chatbot Docker Compose Guide

This guide shows how to run the chatbot stack separately while still connecting to the MCP server when needed.

## 📦 Prerequisites

- Docker Engine 20.10+
- Docker Compose plugin 2.17+
- Cloned repository: `git clone https://github.com/YOUR-ORG/MCP-Oxii.git`

Run all commands from inside the `chatbot/` directory.

## ⚙️ Environment Setup

1. Copy the template environment file:
   ```bash
   cp .env.template .env
   ```
2. Fill in `.env` with your OpenAI API key.

## 🏗️ Build and Run

1. Start the stack:
   ```bash
   docker compose up --build
   ```
   Services launched:
   - `app` – FastAPI chatbot API (port 7000)
   - `oxii-server` – MCP backend (port 9031) built from `../mcp/oxii-server`
   - `redis` – conversation state store (port 6379)
2. Inspect running containers:
   ```bash
   docker compose ps
   ```
3. Check the health endpoint:
   ```bash
   curl http://localhost:7000/health
   ```

## 🔁 Common Commands

| Task | Command |
| --- | --- |
| Rebuild chatbot only | `docker compose build app` |
| Restart chatbot without dependencies | `docker compose up --no-deps --build app` |
| Tail logs | `docker compose logs -f` |
| Tear everything down | `docker compose down` |

## 🧪 Develop Without Docker

```bash
# Terminal 1 – API (stop oxii-server & redis in Compose first)
poetry install
poetry run uvicorn main:app --reload

# Terminal 2 – MCP server
cd ../mcp/oxii-server
poetry install
poetry run python main.py

# Terminal 3 – Redis (optional)
docker compose up redis
```

## 🛟 Troubleshooting

- **Port already in use** – free up ports 7000, 9031, or 6379.
- **Cannot reach MCP server** – confirm `OXII_MCP_SERVER_URL` in `.env` points to `<http://oxii-server:9031>` when running via Compose.
- **Vertex AI auth errors** – ensure `app/service-account.json` exists and is mounted inside the container.
- **Redis connection issues** – verify the `redis` service is up or override `REDIS_URL`.# Chatbot Docker Compose Guide# Chatbot Docker Compose Guide# template Docker Compose Setup



This guide shows how to run the chatbot stack by itself while still wiring in the MCP server for device control.



## 📦 PrerequisitesThis document explains how to build and run the chatbot stack in isolation while still wiring in the MCP server when required.This document provides instructions for running the template blockchain analysis platform using Docker Compose.



- Docker Engine 20.10+

- Docker Compose plugin 2.17+

- Cloned repository: `git clone https://github.com/YOUR-ORG/MCP-Oxii.git`## 📦 Prerequisites## Prerequisites



All commands below assume you are inside the `chatbot/` directory.



## ⚙️ Environment Setup- Docker Engine 20.10+- Docker Engine installed (version 19.03.0+)



1. Copy the sample environment file:- Docker Compose plugin 2.17+- Docker Compose installed (version 1.27.0+)

   ```bash

   cp .env.template .env- Cloned repository: `git clone https://github.com/YOUR-ORG/MCP-Oxii.git`- Git (for cloning the repository)

   ```

2. Update `.env` with your project values. Ensure the Vertex AI service account is stored at `app/service-account.json`.



## 🏗️ Build and RunAll commands below assume you are inside the `chatbot/` folder.## Setup Instructions



1. Bring up the full stack:

   ```bash

   docker compose up --build## ⚙️ Environment1. **Clone the Repository**

   ```

   Services launched:

   - `app` – FastAPI chatbot API (port 7000)

   - `oxii-server` – MCP backend (port 9031) built from `../mcp/oxii-server`1. Copy the sample env file and adjust values as needed:```bash

   - `redis` – chat state store (port 6379)

2. Inspect running containers:   ```bashgit clone <repository-url>

   ```bash

   docker compose ps   cp .env.template .envcd template

   ```

3. Check the health endpoint:   ``````

   ```bash

   curl http://localhost:7000/health2. Ensure `app/service-account.json` contains the Google Vertex AI credentials expected by the agent.

   ```

2. **Configure Environment Variables**

## 🔁 Common Commands

## 🏗️ Build & Run

| Task | Command |

| --- | --- |Copy the template environment file:

| Rebuild chatbot only | `docker compose build app` |

| Restart chatbot without dependencies | `docker compose up --no-deps --build app` |1. Bring the stack up:

| Follow logs | `docker compose logs -f` |

| Tear down everything | `docker compose down` |   ```bash```bash



## 🧪 Local Iteration Without Docker   docker compose up --buildcp .env.template .env



```bash   ``````

# Terminal 1 – API (ensure oxii-server & redis are stopped in Compose)

poetry install

poetry run uvicorn main:app --reload

   Services provisioned:Edit the `.env` file to set your API keys and other configuration parameters:

# Terminal 2 – MCP server

cd ../mcp/oxii-server   - `app` – FastAPI chatbot gateway (port 7000)

poetry install

poetry run python main.py   - `oxii-server` – MCP server (port 9031), built from `../mcp/oxii-server````



# Terminal 3 – Redis (optional)   - `redis` – state backend used by the agentAPI_VERSION=1.0.0

docker compose up redis

```APP_NAME=template



## 🛟 Troubleshooting2. Check service status:OPENAI_API_KEY=your_openai_api_key



- **Port already in use** – stop other services listening on 7000, 9031, or 6379.   ```bashTWITTER_BEARER_TOKEN=your_twitter_bearer_token

- **Cannot reach MCP server** – confirm `OXII_MCP_SERVER_URL` in `.env` points to the running server (default `<http://oxii-server:9031>` when using Compose).

- **Vertex AI auth errors** – check that `app/service-account.json` exists and matches the Google project configured in `.env`.   docker compose psDEBUG_MODE=true

- **Redis connection failures** – make sure the `redis` container is running or override `REDIS_URL`.

   ```BLOCKCHAIN_KNOWLEDGE_MCP_SERVER_URL=http://blockchain-knowledge:9091

ONCHAIN_INSIGHT_MCP_SERVER_URL=http://onchain-insight:9092

3. Confirm the API is healthy:SOCIAL_INSIGHT_MCP_SERVER_URL=http://social-insight:9093

   ```bash```

   curl http://localhost:7000/health

   ```Note: The MCP server URLs have been adjusted to use the Docker Compose service names.



## 🔁 Common Tasks3. **Build and Start the Services**



| Task | Command |```bash

|------|---------|docker-compose up -d

| Rebuild chatbot only | `docker compose build app` |```

| Restart chatbot only | `docker compose up --no-deps --build app` |

| Follow logs | `docker compose logs -f` |This command will:

| Stop stack | `docker compose down` |- Build the Docker images for the main application and all MCP servers

- Create and start containers for each service

## 🧪 Local Iteration Without Docker- Set up the necessary network

- Mount volumes for persistent data storage

You can run services natively for faster feedback:

4. **Verify Services**

```bash

# Terminal 1 – APICheck that all services are running:

docker compose stop oxii-server redis

poetry install```bash

poetry run uvicorn main:app --reloaddocker-compose ps

```

# Terminal 2 – MCP server

cd ../mcp/oxii-serverTest the API health endpoint:

poetry install

poetry run python main.py```bash

curl http://localhost:7000/health

# Terminal 3 – Redis (optional)```

docker compose up redis

```You should receive a response like: `{"status":"healthy"}`



## 🛟 Troubleshooting## Service Access



- **Port already in use** – stop other services using 7000/9031/6379.- Main Application API: http://localhost:7000

- **Cannot reach MCP server** – check `OXII_MCP_SERVER_URL` in `.env` and confirm `oxii-server` container is running.- API Documentation: http://localhost:7000/docs

- **Vertex AI auth errors** – verify `app/service-account.json` matches your Google project and the file is mounted in Docker (`docker compose exec app ls /app`).- Blockchain Knowledge MCP Server: http://localhost:9091

- **Redis connection issues** – ensure the `redis` service is up or adjust `REDIS_URL` in the environment file.- Onchain Insight MCP Server: http://localhost:9092

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