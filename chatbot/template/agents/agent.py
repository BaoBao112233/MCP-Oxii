import os
import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Sequence
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain.tools import Tool, StructuredTool
from langchain.agents import AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from googlesearch import search
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain_core.chat_history import BaseChatMessageHistory
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from template.schemas.chat import ChatRequest, ChatResponse
from template.agents.histories import RedisSupportChatHistory
from template.configs.environment import env
from template.agents.tools.sample_tools import (
    create_plan_tool,
    update_task_status_tool,
    update_plan_status_tool,
    get_plan_by_id_tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_service_account_path(raw_path: str) -> Path:
    """Resolve the service account path for both Docker and local runs."""
    configured_path = Path(raw_path or "")
    candidates = []

    if configured_path.is_absolute():
        candidates.append(configured_path)
        try:
            relative_to_app = configured_path.relative_to("/app")
            candidates.append(PROJECT_ROOT / relative_to_app)
        except ValueError:
            pass
    else:
        candidates.append(PROJECT_ROOT / configured_path)
        candidates.append(Path.cwd() / configured_path)

    if configured_path.name:
        candidates.append(PROJECT_ROOT / "app" / configured_path.name)
        candidates.append(Path.cwd() / "app" / configured_path.name)

    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate

    searched = "\n".join(str(path) for path in candidates if path)
    raise FileNotFoundError(
        "Service account file not found. Checked the following paths:\n" + searched
    )



memories = {}

class MCPAgent:

    def __init__(
        self,
        mcp_server_url: str,
        file_memory_name: str,
        system_prompt: str,
        temperature: float = 0,
        model: Optional[str] = None,
        extra_tools: Optional[Sequence[Union[Tool, StructuredTool]]] = None,
        include_sample_tools: bool = True,
    ):
        # Initialize LLM
        try:
            selected_model = model or env.MODEL_NAME

            self.model = selected_model
            self.llm = ChatOpenAI(
                model=selected_model,
                temperature=temperature,
                openai_api_key=env.OPENAI_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )

            logger.info(
                "Initialized ChatOpenAI with model=%s",
                selected_model
            )
        except Exception as e:
            logger.error(f"Error initializing ChatOpenAI: {str(e)}")
            raise
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ('human',
             [
                {
                    "type": "text",
                    "text": "{input}"
                },
            ]),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        self.mcp_server_url = mcp_server_url
        self.include_sample_tools = include_sample_tools
        self.extra_tools = self._init_extra_tools(extra_tools)

        # Default session and memory
        self.default_session_id = 0
        self.file_memory_name = file_memory_name
        # self.default_system_prompt = system_prompt
        
    # def _get_system_prompt(self) -> str:
    #     """Get the system prompt for the agent"""
    #     return self.default_system_prompt
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request and return a response"""
        try:
            # Get memory for this session
            memory = self._get_memory(
                conversation_id="testing123",
                session_id=request.session_id
            )
            
            prompt = self.prompt
            
            # Try to connect to MCP server with fallback to local tools only
            tools = []
            mcp_connected = False
            
            try:
                async with MultiServerMCPClient(
                    {
                        "mcp-server": {
                            # make sure you start your weather server on port 8000
                            "url": self.mcp_server_url,
                            "transport": "sse",
                        }
                    }
                ) as client:
                    mcp_tools = list(client.get_tools())
                    logger.info("✅ MCP connected - mcp_tools: %s", [tool.name for tool in mcp_tools])
                    tools = self._merge_tools(mcp_tools)
                    mcp_connected = True
                    
                    if self.extra_tools:
                        logger.info(
                            "local_tools: %s",
                            [tool.name for tool in self.extra_tools],
                        )
                        
                    # Create the agent with MCP tools
                    self.agent = OpenAIFunctionsAgent(
                        llm=self.llm,
                        tools=tools,
                        prompt=prompt
                    )
                    
                    # Create the agent executor
                    self.agent_executor = AgentExecutor(
                        agent=self.agent,
                        tools=tools,
                        verbose=True,
                        handle_parsing_errors=True,
                        max_iterations=env.MAX_ITERATIONS
                    )

                    # Set up runnable with chat history
                    agent_with_chat_history = RunnableWithMessageHistory(
                        self.agent_executor,
                        lambda session_id: memory,
                        input_messages_key="input",
                        history_messages_key="chat_history",
                        output_messages_key="output"
                    )
                    
                    # Prepare input data
                    input_data = {
                        "input": json.dumps({
                            "user": request.message,
                            "token": request.token,
                        })
                    }

                    logger.info("input_data: %s", input_data)
                    
                    # Process the message with MCP tools
                    response = await agent_with_chat_history.ainvoke(
                        input_data, 
                        config={
                            "configurable": {"session_id": request.session_id},
                            "run_name": f"Agent:Session{request.session_id}"
                        }
                    )
                    print("-"*10)
                    logger.info("response: %s", response)
                    print("-"*10)
                    # Extract and process the response
                    response_text = response['output']
                    
                    return ChatResponse(
                        response=response_text,
                        tools_used=[tool.name for tool in tools]
                    )
                    
            except Exception as mcp_error:
                logger.warning(f"⚠️ MCP server connection failed: {str(mcp_error)}")
                logger.info("🔄 Falling back to local tools only...")
                
                # Fallback: Use only local tools when MCP is not available
                tools = self.extra_tools if self.extra_tools else []
                
                if not tools:
                    logger.warning("⚠️ No local tools available as fallback")
                    return ChatResponse(
                        response="I'm currently running in limited mode. Some advanced features may not be available. How can I help you with basic operations?",
                        error_status="partial_service"
                    )
                
                logger.info("🛠️ Using local tools as fallback: %s", [tool.name for tool in tools])
                
                # Create the agent with local tools only  
                self.agent = OpenAIFunctionsAgent(
                    llm=self.llm,
                    tools=tools,
                    prompt=prompt
                )
                
                # Create the agent executor
                self.agent_executor = AgentExecutor(
                    agent=self.agent,
                    tools=tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=env.MAX_ITERATIONS
                )

                # Set up runnable with chat history
                agent_with_chat_history = RunnableWithMessageHistory(
                    self.agent_executor,
                    lambda session_id: memory,
                    input_messages_key="input",
                    history_messages_key="chat_history",
                    output_messages_key="output"
                )
                
                # Prepare input data
                input_data = {
                    "input": json.dumps({
                        "user": request.message,
                        "token": request.token,
                    })
                }

                logger.info("input_data (fallback mode): %s", input_data)
                
                # Process the message with local tools only
                response = await agent_with_chat_history.ainvoke(
                    input_data, 
                    config={
                        "configurable": {"session_id": request.session_id},
                        "run_name": f"Agent:Session{request.session_id}:Fallback"
                    }
                )
                
                # Extract and process the response
                response_text = response['output']
                
                return ChatResponse(
                    response=response_text,
                    tools_used=[tool.name for tool in tools],
                    info="Running in fallback mode - some features may be limited"
                )
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)

            return ChatResponse(
                response=f"I encountered an error processing your request. Please try again.",
                error_status="error"
            )


    def _init_extra_tools(
        self,
        extra_tools_input: Optional[Sequence[Union[Tool, StructuredTool]]],
    ) -> List[Union[Tool, StructuredTool]]:
        tools: List[Union[Tool, StructuredTool]] = []

        if self.include_sample_tools:
            tools.extend([create_plan_tool, update_task_status_tool, update_plan_status_tool, get_plan_by_id_tool])

        if extra_tools_input:
            tools.extend(extra_tools_input)

        deduped: List[Union[Tool, StructuredTool]] = []
        seen_names = set()
        for tool in tools:
            name = getattr(tool, "name", None)
            if name and name in seen_names:
                logger.debug("Skipping duplicate tool '%s'", name)
                continue
            if name:
                seen_names.add(name)
            deduped.append(tool)
        return deduped


    def _merge_tools(
        self,
        remote_tools: List[Union[Tool, StructuredTool]],
    ) -> List[Union[Tool, StructuredTool]]:
        if not self.extra_tools:
            return list(remote_tools)

        merged = list(remote_tools)
        remote_names = {getattr(tool, "name", None) for tool in remote_tools}

        for local_tool in self.extra_tools:
            name = getattr(local_tool, "name", None)
            if name and name in remote_names:
                logger.warning("Local tool '%s' ignored because MCP already exposes it.", name)
                continue
            merged.append(local_tool)

        return merged


    def _get_memory(self, session_id: str, conversation_id: str) -> RedisSupportChatHistory:
        """Get or create memory for a session"""    
        session_key = str(session_id)
        if session_key not in memories:
            # Create directory if it doesn't exist
            os.makedirs("memories", exist_ok=True)
            memories[session_key] = RedisSupportChatHistory(
                session_id=session_id,
                conversation_id=conversation_id
            )

            # # Initialize with user ID if it's a new session
            # if not memories[session_key].exists_session():
            #     memories[session_key].add_ai_message(
            #         f"Here we go! Your Conversation ID is {conversation_id}. "
            #         f"I will never give it out again. "
            #         f"It's just for getting more info from tools you need to use. "
            #         f"Input: <token: string>."
            #     )

        return memories[session_key]