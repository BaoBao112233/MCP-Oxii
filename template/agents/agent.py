import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from dexscreener.client import DexscreenerClient
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain.tools import Tool, tool, StructuredTool
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


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

memories = {}

class MCPAgent:
    
    def __init__(self, mcp_server_url: str, openai_api_key: str, file_memory_name: str, system_prompt: str, temperature: float = 0, model: str = "gpt-4o-mini"):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=openai_api_key,
        )
        
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
            memory = self._get_memory(request.session_id)
            
            prompt = self.prompt
            async with MultiServerMCPClient(
                {
                    "mcp-server": {
                        # make sure you start your weather server on port 8000
                        "url": self.mcp_server_url,
                        "transport": "sse",
                    }
                }
            ) as client:
                tools = client.get_tools()
                logger.info(f'mcp_tools: {tool}'for tool in tools)
                # Create the agent
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
                    max_iterations=5
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
                    "input": request.message,
                }
                
                logger.info(f'input_data: {input_data}')
                
                # Process the message
                response = await agent_with_chat_history.ainvoke(
                    input_data, 
                    config={
                        "configurable": {"session_id": request.session_id},
                        "run_name": f"Agent:Session{request.session_id}"
                    }
                )
                
                # Extract and process the response
                response_text = response['output']
                
                # If we manually added the user message, we need to manually add the AI response too
                # if user_message_added:
                #     memory.add_ai_message(response_text)
                
                return ChatResponse(response=response_text)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)

            return ChatResponse(
                response=f"I encountered an error processing your request. Please try again.",
                error_status="error"
            )


    def _get_memory(self, session_id: int) -> FileChatMessageHistory:
        """Get or create memory for a session"""
        session_key = f'{self.file_memory_name}_chat_history_{session_id}'
        file_name = f"memories/{session_key}.json"
        if session_key not in memories:
            # Create directory if it doesn't exist
            os.makedirs("memories", exist_ok=True)
            
            # Initialize with user ID if it's a new session
            memories[session_key] = FileChatMessageHistory(file_name)
            memories[session_key].add_message(BaseMessage(content=f"your user id is {session_id}", type="human"))
            # if not os.path.exists(file_name):

        return memories[session_key]
