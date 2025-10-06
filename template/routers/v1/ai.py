from typing import Optional, Union
from datetime import datetime
import uuid
import os
from fastapi import APIRouter, Depends

from cachetools import TTLCache
from template.agents.agent import MCPAgent
from template.schemas.chat import ChatRequest, ChatResponse
from template.prompt.prompt import DEFAULT_PROMPT
from template.configs.environment import get_environment_variables

env = get_environment_variables()


AgentRouter = APIRouter(
    prefix="/ai", tags=["agent"]
)

cache = TTLCache(maxsize=500, ttl=3600)


@AgentRouter.post("/agent-tmp", response_model=ChatResponse)
async def get_agent(request: ChatRequest):
    agent = MCPAgent(
        mcp_server_url=env.TEMPLATE_MCP_SERVER_URL,
        openai_api_key=env.OPENAI_API_KEY,
        temperature=0.0,
        model="gpt-4o-mini",
        file_memory_name="agent_tmp",
        system_prompt=DEFAULT_PROMPT
    )
    response = await agent.chat(request)
    return response


@AgentRouter.post("/agent-tool-1", response_model=ChatResponse)
async def get_agent(request: ChatRequest):
    agent = MCPAgent(
        mcp_server_url=env.TOOL_1_MCP_SERVER_URL,
        openai_api_key=env.OPENAI_API_KEY,
        temperature=0.0,
        model="gpt-4o-mini",
        file_memory_name="agent_tool_1",
        system_prompt=DEFAULT_PROMPT
    )
    response = await agent.chat(request)
    return response


@AgentRouter.post("/agent-tool-2", response_model=ChatResponse)
async def get_agent(request: ChatRequest):
    agent = MCPAgent(
        mcp_server_url=env.TOOL_2_MCP_SERVER_URL,
        openai_api_key=env.OPENAI_API_KEY,
        temperature=0.0,
        model="gpt-4o-mini",
        file_memory_name="agent_tool_2",
        system_prompt=DEFAULT_PROMPT
    )
    response = await agent.chat(request)
    return response