# OXII Smart Home MCP Server

Modern documentation for the device-control MCP stack that pairs with the FastAPI chatbot. Use this guide the same way you would the chatbot docs: it covers setup, commands, tooling, and troubleshooting for standalone MCP development.

## 🔎 Overview

| | |
| --- | --- |
| **Purpose** | Expose OXII smart home controls (device info, switching, AC, cronjobs, one-touch, room scenarios) via the Model Context Protocol (MCP). |
| **Transport** | Server Sent Events (SSE) on port `9031`. |
| **Runtime** | Python 3.10+, [`mcp.server.FastMCP`](https://github.com/modelcontextprotocol) with LangChain MCP adapters. |
| **Consumers** | The FastAPI chatbot (`chatbot/`) or any MCP-compatible client. |

```text
mcp/oxii-server/
├── main.py            # Boots the FastMCP process and registers tools
├── tools/             # Tool implementations (auth, device control, cronjobs…)
├── client.py          # Quick demo client for manual testing
├── docker-compose.yml # Containerized runtime (exposes :9031)
└── .env.example       # Sample environment for OXII credentials
```

## ✅ Prerequisites

- Python 3.10 or newer (Poetry will manage dependencies), **or** Docker Engine 20.10+
- OXII account credentials with device access (phone, password, country)
- Network access to the OXII staging/prod API defined in `OXII_BASE_URL`

## ⚙️ Environment configuration

Create a working copy of the environment file and fill in the secrets:

```bash
cp .env.example .env
```

| Variable | Description |
| --- | --- |
| `OXII_BASE_URL` | Root URL for the OXII API (staging provided by default). |
| `OXII_PHONE` / `OXII_PASSWORD` / `OXII_COUNTRY` | Login used to obtain access tokens. |
| `PORT` / `HOST` | Optional overrides for where the MCP server listens (default `0.0.0.0:9031`). |
| `DEBUG` | Toggle verbose logging (`true`/`false`). |

## 🚀 Running the server

### Option 1 – Local Poetry workflow

```bash
poetry install
poetry run python main.py
```

This starts the server at `http://localhost:9031/sse`.

### Option 2 – Docker Compose

```bash
cp .env.example .env  # if you have not already
docker compose up --build -d
```

The compose stack exposes port `9031` on the host. Combine this with the chatbot by pointing `OXII_MCP_SERVER_URL` to `http://host.docker.internal:9031/sse` inside the chatbot container.

## ✅ Verifying the service

### 1. Use the bundled client

```bash
poetry run python client.py
```

Select a tool from the prompt and provide the required parameters to confirm end-to-end connectivity.

### 2. Visit the built-in docs UI

- Human friendly docs: `http://host.docker.internal:9031/docx`
- Machine readable catalogue: `http://host.docker.internal:9031/docs.json`

### 3. Curl the SSE handshake

```bash
curl -N http://localhost:9031/sse
```

You should see an initial JSON payload describing the MCP capabilities.

## 🧰 Tool catalogue

Below is a quick reference for each registered MCP tool. All payloads are JSON structures passed through the MCP protocol.

| Tool | Purpose | Key parameters |
| --- | --- | --- |
| `get_device_list` | List homes, rooms, devices, and remote buttons. | `token` |
| `switch_device_control` | Toggle SH1/SH2 relay devices. | `token`, `house_id`, `device_id`, `button_code`, `command` (`ON`/`OFF`) |
| `control_air_conditioner` | Full AC control (mode, temp, fan). | `token`, `serial_number`, `mode`, `fan_speed`, `temperature`, etc. |
| `create_device_cronjob` | Add/update/remove cronjobs for switches or AC. | `token`, `device_id` or `button_id`, `action`, `cron_expression`, `command` |
| `one_touch_control_all_devices` | Execute a house-wide preset (e.g., “turn everything off”). | `token`, `house_id`, `status` |
| `one_touch_control_by_type` | Toggle devices by type (LIGHT, CONDITIONER, …). | `token`, `house_id`, `device_type`, `status` |
| `room_one_touch_control` | Run a single-room preset. | `token`, `room_id`, `status` |

> ℹ️ Detailed schemas live in `tools/` next to each function. Review those modules for argument validation and API payload shapes.

## 🔄 Working with the chatbot

1. Start the MCP server (local or Docker) and ensure port `9031` is reachable from the chatbot environment.
2. In `chatbot/.env`, set `OXII_MCP_SERVER_URL=http://host.docker.internal:9031/sse` when running the chatbot in Docker.
3. Restart the chatbot container (`docker compose restart app`) to apply env changes.
4. Use the chatbot endpoint `POST /ai/agent-oxii` with a valid OXII token—the agent will automatically call the MCP tools.

## 🧪 Testing & diagnostics

- **Unit checks** – Run `poetry run pytest` if you add tests (seed file `test_tools.py` is available as a template).
- **Token validation** – Use `chatbot/test_folders/testing_api.py` to fetch a fresh token before invoking tools.
- **Logs** – With `DEBUG=true`, the server prints detailed traces for each MCP call. In Docker, view them with `docker compose logs -f oxii-server`.

## 🛠 Troubleshooting

| Symptom | Suggested fix |
| --- | --- |
| `httpx.ConnectError: All connection attempts failed` | The consumer is pointing to `localhost` from inside Docker. Use `host.docker.internal` or run both services on the same Compose network. |
| Authentication failures | Double-check `OXII_PHONE`, `OXII_PASSWORD`, and `OXII_COUNTRY`. Tokens expire—fetch a new one if requests start returning 401. |
| Cronjob payload rejected | Ensure the cron expression has 6 fields (`second minute hour day month weekday`) and matches the device type (SH1/SH2 vs SH4). |
| AC commands ignored | Some devices require numeric mode/fan values. See constants in `tools/ac_control.py` for valid ranges. |
| Docker rebuilds are slow | Use `docker compose build oxii-server --no-cache` after dependency changes, otherwise rely on cached layers. |

## 📚 Further reading

- [Model Context Protocol (MCP) specification](https://spec.modelcontextprotocol.io/)
- [LangChain MCP Adapters](https://python.langchain.com/docs/integrations/toolkits/model_context_protocol)
- `chatbot/README.md` for the FastAPI-side integration guide.
