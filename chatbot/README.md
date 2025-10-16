git clone <repository-url>
# MCP-OXII – Smart Home & Crypto Intelligence Platform

## 🚀 Overview

MCP-OXII combines on-chain analytics with OXII smart home automation. The platform exposes LangChain-compatible MCP servers and a FastAPI gateway so agents can fetch token intelligence and control OXII devices through a single conversational interface.

## 🧱 Architecture

```text
├── main.py                      # FastAPI entry point
├── template/                    # Application package
│   ├── agents/agent.py          # OpenAI powered MCP agent
│   ├── routers/v1/ai.py         # HTTP endpoints for chat agents
│   └── configs/environment.py   # Pydantic settings (reads .env)
├── memories/                    # Redis-backed conversation state
├── test_folders/testing_api.py  # Reference scripts for OXII API
└── docker-compose.yml           # Multi-service development stack
```

### Key Components

- **FastAPI Gateway** – serves REST endpoints under `/ai/*` for the chat agents.
- **OpenAI Agent (`template/agents/agent.py`)** – wraps OpenAI GPT via the official OpenAI SDK; uses API key from environment.
- **OXII MCP Server** – Python service powered by `mcp.server.fastmcp.FastMCP` exposing device tools (auth, list devices, switch control, AC control, cronjobs, room one-touch, etc.).

## 🧰 Environment Setup

1. **Clone & install dependencies**

```bash
git clone https://github.com/YOUR-ORG/MCP-Oxii.git
cd MCP-Oxii/chatbot
pip install poetry
poetry install
```

1. **Create environment file**

```bash
cp .env.template .env
```

Fill in the placeholders inside `.env`:

- OpenAI API key (`OPENAI_API_KEY`).
- OXII account credentials (`USER_PHONE`, `USER_PASSWORD`, `USER_COUNTRY`).
- OXII MCP server URL (defaults to the Docker service name).

> The OpenAI API key is set in the `.env` file.

1. **(Optional) Poetry shell**

```bash
poetry shell
```

## 🐳 Running with Docker Compose

```bash
docker compose up --build
```

Services started:

- `app` – FastAPI gateway on port `7000`.
- `redis` – chat memory backend.

> ℹ️ The chatbot expects an MCP server to be available at the URL provided in `OXII_MCP_SERVER_URL` (default `http://host.docker.internal:9031/sse`). Start the MCP stack separately (see below) or point the variable to a remote deployment.

### Starting the MCP stack (Docker)

From `../mcp/oxii-server/`:

```bash
cp .env.example .env
docker compose up --build
```

This launches the OXII MCP server on port `9031`. Once it is running, the chatbot can reach it via the configured `OXII_MCP_SERVER_URL`.

## 🛠️ Local Development (without Docker)

Open three terminals (after loading your Poetry environment):

```bash
# Terminal 1 – start FastAPI
poetry run uvicorn main:app --reload

# Terminal 2 – start OXII MCP server
cd ../mcp/oxii-server
poetry install
poetry run python main.py

# Terminal 3 – inspect available OXII tools
poetry run python client.py
```

## 🧪 OXII MCP Tooling

The MCP server (`../mcp/oxii-server`) is built from `test_folders/testing_api.py` and tool-1/tool-2 conventions:

- `auth.get_oxii_token` – authenticate with phone/password.
- `device_control.get_device_list` / `switch_device_control` – list rooms & toggle devices.
- `ac_control.control_air_conditioner` – full AC payload configuration.
- `one_touch_control` – one-touch house-wide or type-specific toggles.
- `cronjob.create_device_cronjob` – add SH1/SH2/SH4 schedules.
- `room_control.room_one_touch_control` – per-room one-touch execution.

All helpers share a `tools/common.py` utility layer for HTTP calls and polling.

## 🤖 Agent Endpoints

The FastAPI router (`template/routers/v1/ai.py`) exposes:

- `POST /ai/agent-oxii` ← new OpenAI-powered smart home agent

The endpoint instantiates `MCPAgent`, which exclusively uses OpenAI GPT through the API key.

## ✅ Quality Checklist

- OpenAI API key configuration is enforced at agent startup.
- Docker compose instructions cover running the chatbot plus connecting to a separately managed MCP server via `OXII_MCP_SERVER_URL`.
- `test_folders/testing_api.py` kept as a reference, per request.

## 📄 License

Add your preferred license text here.
