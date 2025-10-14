from fastapi import APIRouter, HTTPException
import requests
import json

from template.agents.agent import MCPAgent
from template.schemas.chat import ChatRequest, ChatResponse
from template.configs.environment import env
from template.prompt.prompt import SYSTEM_PROMPT

BASE_URL = env.BASE_URL

AgentRouter = APIRouter(
    prefix="/ai", tags=["agent"]
)

@AgentRouter.post("/agent-oxii", response_model=ChatResponse)
async def get_oxii_agent(request: ChatRequest):
    """OXII Smart Home Control Agent"""

    if not request.token:
        raise HTTPException(status_code=400, detail="Authentication token is required")

    agent = MCPAgent(
        mcp_server_url=env.OXII_MCP_SERVER_URL,
        temperature=0.0,
        model=env.MODEL_NAME,
        file_memory_name="agent_oxii",
        system_prompt=SYSTEM_PROMPT
    )
    response = await agent.chat(request)
    return response

@AgentRouter.post("/get-token", response_model=str)
def get_token(
    user_phone: str,
    user_password: str,
    user_country: str = "VI"
):
    BASE_URL = env.BASE_URL
    url = f"{BASE_URL}/api/app/user/signin"

    payload = json.dumps({
        "phone": user_phone,
        "password": user_password,
        "country": user_country
    })
    headers = {
        'Content-Type': 'application/json',
        'X-Origin': 'smarthiz'
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()
    
    if response['code'] == 200:
        return response['data']['token']
    else:
        return None