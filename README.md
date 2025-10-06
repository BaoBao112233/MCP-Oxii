# template - Blockchain Analysis Platform

## Overview

template is an intelligent analysis platform for blockchain tokens, with a special focus on BASE. The project uses artificial intelligence to analyze and synthesize information about tokens, helping users gain comprehensive and detailed insights about cryptocurrency projects.

## Key Features

- **Token Analysis:** Detailed information about tokens including market value, price fluctuations, token age
- **Liquidity Pool Information:** Analysis of liquidity value and token ratios
- **Bundle Analysis:** Statistics on bundles, number of bundled tokens and percentage of supply
- **KOL Analysis:** Track mentions of tokens by Key Opinion Leaders
- **Twitter Integration:** Search for information about tokens on Twitter
- **Multi-domain Analysis:** Specialized analysis via blockchain knowledge, on-chain insights, and social insights

## Architecture

template uses a modular architecture with these main components:

- **FastAPI Backend:** Handles HTTP requests and serves API endpoints
- **MCPAgent:** Core AI agent that processes user queries using LangChain
- **MCP Servers:** Specialized servers for domain-specific analysis:
  - `blockchain-knowledge`: General blockchain information
  - `onchain-insight`: Analysis of on-chain data
  - `social-insight`: Social media and sentiment analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd template
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install poetry
poetry install
```

4. Set up environment variables:
```bash
cp .env.template .env
```

Edit the `.env` file and add the following variables:
```
API_VERSION=v1
APP_NAME=template
OPENAI_API_KEY=your_openai_api_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
KOL_BASE_URL=your_kol_base_url
SIMILAR_BASE_URL=your_similar_base_url
DEBUG_MODE=True
MCP_SERVER_URL=your_mcp_server_url
```

## Running the Application

### Start the FastAPI Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 7000 --reload
```

For production with multiple workers:

```bash
uvicorn main:app --host 0.0.0.0 --port 7000 --workers 8
```

The server will be available at: http://0.0.0.0:7000

### API Documentation

- API documentation is available at: http://0.0.0.0:7000/docs
- Health check endpoint: http://0.0.0.0:7000/health

## API Endpoints

- **GET /ai/agent-blockchain-knowledge**: Access blockchain knowledge agent
- **GET /ai/agent-onchain-insight**: Access on-chain insight agent
- **GET /ai/agent-social-insight**: Access social insight agent

## Project Structure

```
template/
├── template/                # Core package
│   ├── agents/             # AI agents implementation
│   ├── configs/            # Environment and configuration settings
│   ├── routers/            # API routes
│   └── schemas/            # Data models and schemas
├── mcp-servers/            # MCP server implementations
│   ├── blockchain-knowledge/
│   ├── onchain-insight/
│   └── social-insight/
├── memories/               # Persistent chat memories
├── main.py                 # Application entry point
└── pyproject.toml          # Project dependencies
```

## Development

### Running MCP Servers

Each MCP server can be run independently to work on specific domain analysis:

```bash
cd mcp-servers/blockchain-knowledge
python main.py
```

### Adding New Features

1. Update the appropriate MCP server with new analysis capabilities
2. Add new tools to the MCPAgent in template/agents/agent.py
3. Update the system prompt to incorporate new capabilities

## License

[Specify your project license here]
