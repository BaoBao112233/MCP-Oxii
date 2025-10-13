from fastapi import APIRouter, HTTPException
import requests
import json

from template.agents.agent import MCPAgent
from template.schemas.chat import ChatRequest, ChatResponse
from template.configs.environment import env


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
        system_prompt="""You are an OXII Smart Home Assistant. You help users control their smart home devices including:
        
        - Switches and lights
        - Air conditioners with temperature and mode control
        - Scheduling devices with cronjobs
        - One-touch control for all devices or by device type
        - Room-level device control
        
        Always ask for authentication token first if not provided. Be helpful and explain what each control option does.
        
        Available device types: LIGHT, TV, CONDITIONER, FAN, HOT_COLD_SHOWER, SOCKET
        Available AC modes: 1=auto, 2=heat, 3=cool, 4=dry, 5=fan
        Available fan speeds: 0=auto, 1=low, 2=medium, 3=high, 4=turbo
        
        For cronjobs, use 6-field cron format: second minute hour day month weekday
        Example: "0 30 8 * * 1-5" means 8:30 AM on weekdays
        """
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