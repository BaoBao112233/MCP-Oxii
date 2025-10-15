import logging
import requests
import json
import time
import os
from typing import Dict, Any, List, Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from datetime import datetime
from dataclasses import dataclass
from template.configs.environment import env

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Represents a task within a plan."""
    order_no: int
    title: str
    description: str
    max_retries: int = 2
    id: Optional[int] = None
    status: str = "pending"
    execution_result: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Plan:
    """Represents a planning structure for GraphQL API."""
    session_id: int
    title: str
    goal_text: str
    trigger: str = "SYSTEM"
    priority: int = 1
    tasks: List[Task] = None
    id: Optional[int] = None
    status: str = "created"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
    
    def to_graphql_format(self) -> Dict[str, Any]:
        """Convert Plan to GraphQL mutation format."""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "goal_text": self.goal_text,
            "trigger": self.trigger,
            "priority": self.priority,
            "tasks": {
                "data": [
                    {
                        "order_no": task.order_no,
                        "title": task.title,
                        "description": task.description,
                        "max_retries": task.max_retries
                    }
                    for task in self.tasks
                ]
            }
        }


class PlannerAPIClient:
    """Client for interacting with the Planner GraphQL API."""

    def __init__(self, base_url: str = env.PLANNING_API_URL, admin_secret: str = env.PLANNING_API_KEY):
        self.base_url = base_url
        self.graphql_endpoint = f"{base_url}"
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'content-type': 'application/json',
            'origin': base_url,
            'priority': 'u=1, i',
            'referer': f'{base_url}/console',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'x-hasura-admin-secret': admin_secret
        }
    
    def execute_graphql(self, query: str, variables: Optional[Dict] = None, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Execute a GraphQL query/mutation."""
        payload = {
            "query": query,
            "variables": variables,
            "operationName": operation_name
        }
        
        try:
            response = requests.post(
                self.graphql_endpoint,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "errors": [{"message": f"Network error: {str(e)}"}],
                "data": None
            }


def create_plan_via_graphql(
    session_id: int,
    plans: List[Plan],
    api_client: Optional[PlannerAPIClient] = None
) -> Dict[str, Any]:
    """
    Create multiple plans using GraphQL API.
    
    Args:
        session_id: Session ID for the plans
        plans: List of Plan objects to create
        api_client: Optional API client instance
        
    Returns:
        Dict containing the API response with created plans
    """
    if api_client is None:
        api_client = PlannerAPIClient()
    
    # Convert plans to GraphQL format
    plan_objects = []
    for plan in plans:
        plan.session_id = session_id  # Ensure session_id is set
        plan_objects.append(plan.to_graphql_format())
    
    # Build GraphQL mutation
    mutation = """
    mutation createPlan {
        insert_planner_plans(objects: %s) {
            affected_rows
            returning {
                id
                title
                goal_text
                trigger
                priority
                status
                created_at
                updated_at
                tasks {
                    id
                    order_no
                    title
                    description
                    max_retries
                    status
                    created_at
                    updated_at
                }
            }
        }
    }
    """ % json.dumps(plan_objects)
    
    # Execute mutation
    result = api_client.execute_graphql(mutation, operation_name="createPlan")
    
    if "errors" in result and result["errors"]:
        return {
            "success": False,
            "error": result["errors"][0]["message"],
            "plans_created": 0,
            "data": None
        }
    
    # Process successful response
    insert_result = result.get("data", {}).get("insert_planner_plans", {})
    affected_rows = insert_result.get("affected_rows", 0)
    created_plans = insert_result.get("returning", [])
    
    return {
        "success": True,
        "plans_created": affected_rows,
        "data": created_plans,
        "message": f"Successfully created {affected_rows} plan(s)"
    }


def update_execute_plan_via_graphql(
    plan_id: int,
    task_id: int,
    status: str = "completed",
    execution_result: Optional[str] = None,
    api_client: Optional[PlannerAPIClient] = None
) -> Dict[str, Any]:
    """
    Update the execution status of a specific task in a plan.
    
    Args:
        plan_id: ID of the plan containing the task
        task_id: ID of the task to update
        status: New status for the task (pending, in_progress, completed, failed)
        execution_result: Optional result description of the task execution
        api_client: Optional API client instance
        
    Returns:
        Dict containing the API response with updated task
    """
    if api_client is None:
        api_client = PlannerAPIClient()
    
    # Validate status
    valid_statuses = ["pending", "in_progress", "completed", "failed", "skipped"]
    if status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status '{status}'. Valid options: {', '.join(valid_statuses)}",
            "data": None
        }
    
    # Build update object
    update_object = {
        "status": status,
        "updated_at": datetime.now().isoformat()
    }
    
    if execution_result:
        update_object["execution_result"] = execution_result
    
    # Build GraphQL mutation
    mutation = """
    mutation updateTaskExecution {
        update_planner_tasks(
            where: {
                id: {_eq: %d},
                plan_id: {_eq: %d}
            },
            _set: %s
        ) {
            affected_rows
            returning {
                id
                order_no
                title
                description
                status
                execution_result
                max_retries
                created_at
                updated_at
                plan {
                    id
                    title
                    session_id
                    status
                }
            }
        }
    }
    """ % (task_id, plan_id, json.dumps(update_object))
    
    # Execute mutation
    result = api_client.execute_graphql(mutation, operation_name="updateTaskExecution")
    
    if "errors" in result and result["errors"]:
        return {
            "success": False,
            "error": result["errors"][0]["message"],
            "tasks_updated": 0,
            "data": None
        }
    
    # Process successful response
    update_result = result.get("data", {}).get("update_planner_tasks", {})
    affected_rows = update_result.get("affected_rows", 0)
    updated_tasks = update_result.get("returning", [])
    
    if affected_rows == 0:
        return {
            "success": False,
            "error": f"Task {task_id} not found in plan {plan_id}",
            "tasks_updated": 0,
            "data": None
        }
    
    return {
        "success": True,
        "tasks_updated": affected_rows,
        "data": updated_tasks[0] if updated_tasks else None,
        "message": f"Successfully updated task {task_id} to status '{status}'"
    }


# ========== DEVICE CONTROL FUNCTIONS ==========

def execute_device_command(device_name: str, command: str, room: str) -> Dict[str, Any]:
    """
    Execute a command on a device.
    This is a mock implementation - in real system, this would send command to device.
    
    Args:
        device_name: Name of the device
        command: Command to execute (e.g., "bật", "tắt")
        room: Room where the device is located
        
    Returns:
        Dict with execution result
    """
    logger.info(f"🔧 Executing command '{command}' on {device_name} in {room}")
    
    # Mock command execution - in real implementation, this would send command to device
    # Simulate some delay and success/failure
    time.sleep(0.5)  # Simulate command execution time
    
    # For demo, assume command succeeds
    return {
        "success": True,
        "device": device_name,
        "command": command,
        "room": room,
        "message": f"Command '{command}' executed on {device_name}"
    }


def parse_command_from_task(task_title: str) -> Dict[str, Any]:
    """
    Parse device command from task title.
    
    Args:
        task_title: Task title (e.g., "Bật đèn phòng khách")
        
    Returns:
        Dict with parsed command information
    """
    title_lower = task_title.lower()
    
    # Extract device name
    devices = ["đèn", "quạt", "điều hòa", "camera", "cảm biến", "loa"]
    device_name = None
    for device in devices:
        if device in title_lower:
            device_name = device
            break
    
    # Extract command
    commands = ["bật", "tắt", "kích hoạt", "tăng", "giảm", "kiểm tra"]
    command = None
    for cmd in commands:
        if cmd in title_lower:
            command = cmd
            break
    
    # Extract room (if mentioned)
    rooms = ["phòng khách", "phòng ngủ", "phòng bếp", "living_room", "bedroom", "kitchen"]
    room = "unknown"
    for r in rooms:
        if r in title_lower:
            room = r
            break
    
    return {
        "device_name": device_name,
        "command": command,
        "room": room,
        "task_title": task_title
    }


# ========== PLANNING TOOLS ==========

class CreatePlanInput(BaseModel):
    """Input schema for creating a plan."""
    task_description: str = Field(..., description="Description of the main task to create a plan for")
    max_steps: int = Field(default=5, description="Maximum number of steps in the plan")
    room: str = Field(default="living_room", description="Room where the plan will be executed")
    priority: str = Field(default="medium", description="Priority level: low, medium, high")
    session_id: int = Field(default=1, description="Session ID for the plan")

def create_plan_function(task_description: str, max_steps: int = 5, room: str = "living_room", priority: str = "medium", session_id: int = 1) -> str:
    """
    Create a structured plan for a given task using GraphQL API.
    Returns a simple string response to avoid function call/response mismatch.
    """
    try:
        logger.info(f"🚀 Creating plan for task: {task_description} in room: {room}")
        
        # Generate plan steps based on task description
        if "security" in task_description.lower() or "an ninh" in task_description.lower():
            plan_steps = [
                Task(order_no=1, title=f"Kiểm tra camera an ninh trong {room}", description=f"Kiểm tra camera an ninh trong {room}"),
                Task(order_no=2, title=f"Kích hoạt cảm biến chuyển động trong {room}", description=f"Kích hoạt cảm biến chuyển động trong {room}"),
                Task(order_no=3, title=f"Bật đèn cảnh báo trong {room}", description=f"Bật đèn cảnh báo trong {room}"),
                Task(order_no=4, title=f"Phát cảnh báo âm thanh qua loa", description="Phát cảnh báo âm thanh qua loa"),
                Task(order_no=5, title=f"Gửi thông báo đến điện thoại", description="Gửi thông báo đến điện thoại")
            ]
        elif "điều hòa" in task_description.lower() or "conditioner" in task_description.lower():
            plan_steps = [
                Task(order_no=1, title=f"Kiểm tra trạng thái điều hòa trong {room}", description=f"Kiểm tra trạng thái điều hòa trong {room}"),
                Task(order_no=2, title=f"Điều chỉnh nhiệt độ phù hợp", description="Điều chỉnh nhiệt độ phù hợp"),
                Task(order_no=3, title=f"Bật/tắt điều hòa theo yêu cầu", description="Bật/tắt điều hòa theo yêu cầu"),
                Task(order_no=4, title=f"Kiểm tra và báo cáo tình trạng", description="Kiểm tra và báo cáo tình trạng")
            ]
        elif "đèn" in task_description.lower() or "light" in task_description.lower():
            plan_steps = [
                Task(order_no=1, title=f"Kiểm tra trạng thái đèn trong {room}", description=f"Kiểm tra trạng thái đèn trong {room}"),
                Task(order_no=2, title=f"Bật/tắt đèn theo yêu cầu", description="Bật/tắt đèn theo yêu cầu"),
                Task(order_no=3, title=f"Điều chỉnh độ sáng nếu cần", description="Điều chỉnh độ sáng nếu cần"),
                Task(order_no=4, title=f"Xác nhận trạng thái cuối cùng", description="Xác nhận trạng thái cuối cùng")
            ]
        else:
            # Generic plan
            plan_steps = [
                Task(order_no=1, title=f"Phân tích yêu cầu: {task_description}", description=f"Phân tích yêu cầu: {task_description}"),
                Task(order_no=2, title=f"Kiểm tra thiết bị khả dụng trong {room}", description=f"Kiểm tra thiết bị khả dụng trong {room}"),
                Task(order_no=3, title=f"Thực hiện hành động chính", description="Thực hiện hành động chính"),
                Task(order_no=4, title=f"Kiểm tra kết quả và báo cáo", description="Kiểm tra kết quả và báo cáo")
            ]
        
        # Limit to max_steps
        plan_steps = plan_steps[:max_steps]
        
        # Create Plan object
        plan = Plan(
            session_id=session_id,
            title=f"Plan: {task_description}",
            goal_text=f"Automated plan for {task_description} in {room}",
            trigger="SYSTEM",
            priority=1 if priority == "high" else 2 if priority == "medium" else 3,
            tasks=plan_steps
        )
        
        # Try API call
        api_result = create_plan_via_graphql(session_id, [plan])
        
        if api_result["success"]:
            created_plans = api_result["data"]
            if created_plans:
                plan_data = created_plans[0]
                task_descriptions = [task["title"] for task in plan_data["tasks"]]
                
                return f"✅ Plan created successfully!\n" \
                       f"Plan ID: {plan_data['id']}\n" \
                       f"Task: {task_description}\n" \
                       f"Room: {room}\n" \
                       f"Priority: {priority}\n" \
                       f"Total Steps: {len(plan_data['tasks'])}\n" \
                       f"Steps:\n" + "\n".join([f"  {i+1}. {step}" for i, step in enumerate(task_descriptions)]) + \
                       f"\n\nService: Connected to GraphQL API"
        else:
            # Service unavailable - return local plan without API
            logger.warning(f"⚠️ GraphQL API unavailable, creating local plan")
            task_descriptions = [task.title for task in plan_steps]
            
            return f"✅ Local plan created (API unavailable)!\n" \
                   f"Task: {task_description}\n" \
                   f"Room: {room}\n" \
                   f"Priority: {priority}\n" \
                   f"Total Steps: {len(plan_steps)}\n" \
                   f"Steps:\n" + "\n".join([f"  {i+1}. {step}" for i, step in enumerate(task_descriptions)]) + \
                   f"\n\nNote: GraphQL API is currently unavailable. Plan created locally."
        
    except Exception as e:
        logger.error(f"❌ Plan creation failed for '{task_description}': {str(e)}")
        return f"❌ Plan creation failed: {str(e)}"


# ========== EXECUTION TOOLS ==========

class ExecuteStepInput(BaseModel):
    """Input schema for executing a plan step."""
    plan_id: int = Field(..., description="ID of the plan containing the step")
    step_id: int = Field(..., description="ID of the specific step to execute")
    action: str = Field(default="execute", description="Action to perform: execute, start, complete, fail, retry")
    result: str = Field(default="", description="Result message for the step execution")
    enable_retry: bool = Field(default=True, description="Whether to automatically retry failed steps")

def execute_step_function(plan_id: int, step_id: int, status: str = "completed", results: str = "") -> str:
    """
    Execute a plan step with retry logic for failed device commands.
    Returns a simple string response to avoid function call/response mismatch.
    """
    MAX_RETRIES = 3
    
    try:
        logger.info(f"🔄 Executing step {step_id} in plan {plan_id}")
        
        # First, get task information to understand what to execute
        # We need to query the task details from the API
        api_client = PlannerAPIClient()
        
        # Query to get task details
        query = """
        query getTask {
            planner_tasks(where: {id: {_eq: %d}, plan_id: {_eq: %d}}) {
                id
                title
                description
                status
                execution_result
            }
        }
        """ % (step_id, plan_id)
        
        result = api_client.execute_graphql(query, operation_name="getTask")
        
        if "errors" in result and result["errors"]:
            return f"❌ Failed to get task information: {result['errors'][0]['message']}"
        
        tasks = result.get("data", {}).get("planner_tasks", [])
        if not tasks:
            return f"❌ Task {step_id} not found in plan {plan_id}"
        
        task = tasks[0]
        task_title = task["title"]
        
        # Parse command from task title
        parsed_command = parse_command_from_task(task_title)
        device_name = parsed_command["device_name"]
        command = parsed_command["command"]
        room = parsed_command["room"]
        
        if not device_name or not command:
            # Not a device command, just update status normally
            logger.info(f"📝 Task {step_id} is not a device command, updating status to {status}")
            api_result = update_execute_plan_via_graphql(plan_id, step_id, status, results)
            
            if api_result["success"]:
                task_data = api_result["data"]
                return f"✅ Step updated successfully!\n" \
                       f"Plan ID: {plan_id}\n" \
                       f"Step ID: {step_id}\n" \
                       f"New Status: {task_data['status']}\n" \
                       f"Results: {task_data['execution_result'] or results}\n" \
                       f"Service: Connected to GraphQL API"
            else:
                return f"❌ Step update failed: {api_result['error']}"
        
        # Execute device command with retry logic
        logger.info(f"🔧 Executing device command: {command} {device_name} in {room}")
        
        for attempt in range(MAX_RETRIES):
            logger.info(f"🔄 Attempt {attempt + 1}/{MAX_RETRIES} for step {step_id}")
            
            # Execute the device command
            execute_result = execute_device_command(device_name, command, room)
            
            if execute_result["success"]:
                # Success! Update task status
                api_result = update_execute_plan_via_graphql(plan_id, step_id, "completed", 
                                                           f"Command '{command}' executed successfully on {device_name}")
                
                if api_result["success"]:
                    task_data = api_result["data"]
                    return f"✅ Step completed successfully!\n" \
                           f"Plan ID: {plan_id}\n" \
                           f"Step ID: {step_id}\n" \
                           f"Command: {command} {device_name}\n" \
                           f"Attempts: {attempt + 1}\n" \
                           f"Service: Connected to GraphQL API"
                else:
                    return f"❌ Step execution succeeded but status update failed: {api_result['error']}"
            else:
                logger.warning(f"❌ Command execution failed on attempt {attempt + 1}")
                if attempt == MAX_RETRIES - 1:
                    # Mark task as failed after all retries
                    api_result = update_execute_plan_via_graphql(plan_id, step_id, "failed", 
                                                               f"Command execution failed after {MAX_RETRIES} attempts")
                    return f"❌ Step failed after {MAX_RETRIES} attempts!\n" \
                           f"Plan ID: {plan_id}\n" \
                           f"Step ID: {step_id}\n" \
                           f"Command: {command} {device_name}\n" \
                           f"Reason: Command execution failed"
        
        # This should not be reached, but just in case
        return f"❌ Unexpected error in step execution"
        
    except Exception as e:
        logger.error(f"❌ Step execution failed for plan {plan_id}, step {step_id}: {str(e)}")
        return f"❌ Step execution failed: {str(e)}"


# ========== STRUCTURED TOOLS ==========

# Planning Agent Tools
create_plan_tool = StructuredTool.from_function(
    func=create_plan_function,
    name="create_plan",
    description="Create a structured plan with steps for accomplishing a given task using GraphQL API. The plan will be stored in the service and can be tracked through execution.",
    args_schema=CreatePlanInput
)

# Executor Agent Tools  
execute_step_tool = StructuredTool.from_function(
    func=execute_step_function,
    name="execute_step", 
    description="Execute or update status of a single step from a plan using GraphQL API. Use this to start, complete, or fail individual tasks from plans created by the Planning Agent.",
    args_schema=ExecuteStepInput
)


if __name__ == "__main__":
    # Simple test
    test_plan_response = create_plan_function(
        task_description="Bật đèn phòng khách và điều hòa",
        max_steps=4,
        room="phòng khách",
        priority="high",
        session_id=1
    )
    print(test_plan_response)
    
    # Assuming a plan and step ID for testing execution
    test_execute_response = execute_step_function(
        plan_id=1,
        step_id=1,
        status="completed",
        results="Test execution of step"
    )
    print(test_execute_response)