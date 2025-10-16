import logging
from typing import Dict, Any, List
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import requests
import json
from template.configs.environment import env

logger = logging.getLogger(__name__)

# ========== PLANNING TOOLS ==========

class CreatePlanInput(BaseModel):
    """Input schema for creating a plan."""
    title_plan: str = Field(..., description="Title of the plan")
    goal_plan: str = Field(..., description="Goal of the plan")
    list_tasks: List[Dict[str, Any]] = Field(..., description="List of tasks with title and description")

def create_plan_function(title_plan: str, goal_plan: str, list_tasks: List[Dict[str, Any]]) -> str:
    """
    Create a structured plan for a given task using the GraphQL API.
    This tool helps the Planning Agent break down complex tasks into actionable steps.
    
    Args:
        task_description: The main task to create a plan for
        max_steps: Maximum number of steps (default: 5)
        
    Returns:
        Dictionary with the created plan from API
    """
    try:
        logger.info(f"Creating plan: {title_plan}")
        
        # Generate plan steps
        max_steps = len(list_tasks)
        plan_steps = [
            {"order_no": i+1, "title": f"Step {i+1}: Analyze the requirement - {list_tasks[i]['title']}", "description": f"{list_tasks[i]['description']}", "max_retries": 2}
            for i in range(max_steps)
        ]
        
        # Build GraphQL mutation
        mutation = """
        mutation createPlan($objects: [planner_plans_insert_input!]!) {
            insert_planner_plans(objects: $objects) {
                affected_rows
                returning {
                    id
                    title
                    goal_text
                    trigger
                    priority
                    tasks {
                        id
                        order_no
                        title
                        description
                        max_retries
                    }
                }
            }
        }
        """
        
        variables = {
            "objects": [{
                "session_id": 1,
                "title": f"Plan for {title_plan}",
                "goal_text": goal_plan,
                "trigger": "SYSTEM",
                "priority": 1,
                "tasks": {
                    "data": plan_steps
                }
            }]
        }
        
        payload = {
            "query": mutation,
            "variables": variables,
            "operationName": "createPlan"
        }
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://ow-subscription-api.smarthiz.com',
            'priority': 'u=1, i',
            'referer': 'https://ow-subscription-api.smarthiz.com/console',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'x-hasura-admin-secret': env.PLANNING_API_KEY
        }
        
        response = requests.post(env.PLANNING_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                return f"Task '{title_plan}' creation failed: {data['errors']}"
            else:
                return f"Task '{title_plan}' created successfully with ID: {data['data']['insert_planner_plans']['returning'][0]['id']}"
        else:
            return f"Task '{title_plan}' creation failed: HTTP error: {response.status_code} - {response.text}"
        
    except Exception as e:
        return f"Plan creation failed for '{title_plan}': {str(e)}"

# ========== EXECUTION TOOLS ==========

class UpdateTaskStatusInput(BaseModel):
    """Input schema for updating task status."""
    task_id: str = Field(..., description="ID of the task to update")
    status: str = Field(..., description="New status for the task (e.g., 'DONE', 'FAILED')")

class UpdatePlanStatusInput(BaseModel):
    """Input schema for updating plan status."""
    plan_id: str = Field(..., description="ID of the plan to update")
    status: str = Field(..., description="New status for the plan (e.g., 'RUNNING', 'DONE')")

def update_task_status_function(task_id: str, status: str) -> str:
    """
    Update the status of a task in the plan.
    
    Args:
        task_id: ID of the task
        status: New status
        
    Returns:
        Dictionary with update result
    """
    try:
        logger.info(f"Updating task {task_id} to status: {status}")
        
        # Assume mutation for updating task status
        query = f"""
        mutation UpdateStatusTasks {{
            update_planner_tasks_by_pk(pk_columns: {{id: \"{task_id}\"}}, _set: {{status: \"{status}\"}}) {{
                id
                order_no
                title
                description
                max_retries
                status
            }}
        }}
        """

        payload = {
            "query": query,
            "variables": None,
            "operationName": "UpdateStatusTasks"
        }
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://ow-subscription-api.smarthiz.com',
            'priority': 'u=1, i',
            'referer': 'https://ow-subscription-api.smarthiz.com/console',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'x-hasura-admin-secret': env.PLANNING_API_KEY
        }

        response = requests.post(env.PLANNING_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                return f"Task '{task_id}' update failed: {data['errors']}"
            else:
                return f"Task '{task_id}' updated successfully to status: {status}"
        else:
            return f"Task '{task_id}' update failed: HTTP error: {response.status_code} - {response.text}"
        
    except Exception as e:
        return f"Task update failed for '{task_id}': {str(e)}"

def update_plan_status_function(plan_id: str, status: str) -> str:
    """
    Update the status of a plan.
    
    Args:
        plan_id: ID of the plan
        status: New status
        
    Returns:
        Update result message
    """
    try:
        logger.info(f"Updating plan {plan_id} to status: {status}")
        
        # Build GraphQL mutation
        mutation = f"""
        mutation UpdateStatusPlans {{
            update_planner_plans_by_pk(pk_columns: {{ id: \"{plan_id}\" }}, _set: {{ status: \"{status}\" }}) {{
                id
                title
                goal_text
                trigger
                priority
                status
                tasks {{
                    id
                    order_no
                    title
                    description
                    max_retries
                    status
                }}
            }}
        }}
        """
        payload = {
            "query": mutation,
            "variables": None,
            "operationName": "UpdateStatusPlans"
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://ow-subscription-api.smarthiz.com',
            'priority': 'u=1, i',
            'referer': 'https://ow-subscription-api.smarthiz.com/console',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'x-hasura-admin-secret': env.PLANNING_API_KEY
        }

        response = requests.post(env.PLANNING_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                return f"Plan '{plan_id}' update failed: {data['errors']}"
            else:
                return f"Plan '{plan_id}' updated successfully to status: {status}"
        else:
            return f"Plan '{plan_id}' update failed: HTTP error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Plan update failed for '{plan_id}': {str(e)}"

# ========== TOOLS REGISTRATION =========

class GetPlanByIdInput(BaseModel):
    """Input schema for getting plan by ID."""
    plan_id: str = Field(..., description="ID of the plan to retrieve")

def get_plan_by_id_function(plan_id: str) -> str:
    """
    Retrieve a plan by its ID.
    
    Args:
        plan_id: ID of the plan to retrieve
        
    Returns:
        Dictionary with the retrieved plan
    """
    try:
        logger.info(f"Retrieving plan with ID: {plan_id}")

        query = f"query GetPlanById {{ planner_plans_by_pk(id: \"{plan_id}\") {{ id title goal_text trigger priority status tasks {{ id order_no title description max_retries status }} }} }}"
        payload = {
            "query": query,
            "variables": None,
            "operationName": "GetPlanById"
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://ow-subscription-api.smarthiz.com',
            'priority': 'u=1, i',
            'referer': 'https://ow-subscription-api.smarthiz.com/console',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'x-hasura-admin-secret': env.PLANNING_API_KEY
        }

        response = requests.post(env.PLANNING_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                return f"Plan '{plan_id}' retrieval failed: {data['errors']}"
            else:
                return f"Plan '{plan_id}' retrieved successfully: {data['data']}"
        else:
            return f"Plan '{plan_id}' retrieval failed: HTTP error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Plan retrieval failed for '{plan_id}': {str(e)}"

# ========== STRUCTURED TOOLS ==========

create_plan_tool = StructuredTool.from_function(
    func=create_plan_function,
    name="create_plan",
    description="""
    Create a structured plan for a given task using the GraphQL API.
    This tool helps the Planning Agent break down complex tasks into actionable steps.
    """,
    args_schema=CreatePlanInput
)

    # Input:
    # - title_plan: Title of the plan (string)
    # - goal_plan: Goal of the plan (string)
    # - list_tasks: List of tasks with title and description (list of dicts):
    #     - title: Title of the task (string)
    #     - description: Description of the task (string)

# Update Task Status Tool
update_task_status_tool = StructuredTool.from_function(
    func=update_task_status_function,
    name="update_task_status",
    description="""
    Update the status of a task in the plan.
    """,
    args_schema=UpdateTaskStatusInput
)

update_plan_status_tool = StructuredTool.from_function(
    func=update_plan_status_function,
    name="update_plan_status",
    description="Update the status of a plan.",
    args_schema=UpdatePlanStatusInput
)

get_plan_by_id_tool = StructuredTool.from_function(
    func=get_plan_by_id_function,
    name="get_plan_by_id",
    description="Retrieve a plan by its ID.",
    args_schema=GetPlanByIdInput
)
