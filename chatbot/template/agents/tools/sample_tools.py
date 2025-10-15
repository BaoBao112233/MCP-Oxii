import logging
from typing import Dict, Any, List
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

try:
    from googlesearch import search
except ImportError:
    def search(*args, **kwargs):
        return ["Google search not available - install googlesearch-python"]

logger = logging.getLogger(__name__)

# ========== PLANNING TOOLS ==========

class CreatePlanInput(BaseModel):
    """Input schema for creating a plan."""
    task_description: str = Field(..., description="Description of the main task to create a plan for")
    max_steps: int = Field(default=5, description="Maximum number of steps in the plan")

def create_plan_function(task_description: str, max_steps: int = 5) -> Dict[str, Any]:
    """
    Create a structured plan for a given task.
    This tool helps the Planning Agent break down complex tasks into actionable steps.
    
    Args:
        task_description: The main task to create a plan for
        max_steps: Maximum number of steps (default: 5)
        
    Returns:
        Dictionary with the created plan
    """
    try:
        logger.info(f"Creating plan for task: {task_description}")
        
        # This is a template - in real implementation, this could use LLM to generate better plans
        plan_steps = [
            f"Step 1: Analyze the requirement - {task_description}",
            f"Step 2: Research relevant information",
            f"Step 3: Gather necessary resources", 
            f"Step 4: Execute the main task",
            f"Step 5: Review and finalize results"
        ]
        
        # Limit to max_steps
        plan_steps = plan_steps[:max_steps]
        
        result = {
            "task": task_description,
            "plan_steps": plan_steps,
            "total_steps": len(plan_steps),
            "status": "success",
            "message": f"Created plan with {len(plan_steps)} steps"
        }
        
        logger.info(f"Plan created successfully for: {task_description}")
        return result
        
    except Exception as e:
        error_result = {
            "task": task_description,
            "plan_steps": [],
            "status": "error",
            "message": f"Plan creation failed: {str(e)}"
        }
        logger.error(f"Plan creation failed for '{task_description}': {str(e)}")
        return error_result

# ========== EXECUTION TOOLS ==========

class ExecuteStepInput(BaseModel):
    """Input schema for executing a plan step."""
    step_description: str = Field(..., description="Description of the step to execute")
    step_number: int = Field(..., description="The step number in the plan")

def execute_step_function(step_description: str, step_number: int) -> Dict[str, Any]:
    """
    Execute a single step from a plan.
    This tool helps the Executor Agent complete individual steps.
    
    Args:
        step_description: Description of the step to execute
        step_number: The step number in the plan
        step_status: Current status of the step ("failed", "in_progress", "completed")
        
    Returns:
        Dictionary with execution results
    """
    try:
        logger.info(f"Executing step {step_number}: {step_description}")
        
        # Simulate step execution - in real implementation, this would perform actual actions
        result = {
            "step_number": step_number,
            "step_description": step_description, 
            "execution_result": f"Successfully completed: {step_description}",
            "status": "completed",
            "message": f"Step {step_number} executed successfully"
        }
        
        logger.info(f"Step {step_number} completed successfully")
        return result
        
    except Exception as e:
        error_result = {
            "step_number": step_number,
            "step_description": step_description,
            "execution_result": "",
            "status": "failed", 
            "message": f"Step execution failed: {str(e)}"
        }
        logger.error(f"Step {step_number} execution failed: {str(e)}")
        return error_result

# ========== STRUCTURED TOOLS ==========

# Planning Agent Tools
create_plan_tool = StructuredTool.from_function(
    func=create_plan_function,
    name="create_plan",
    description="Create a structured plan with steps for accomplishing a given task. Use this to break down complex requests into actionable steps.",
    args_schema=CreatePlanInput
)

# Executor Agent Tools  
execute_step_tool = StructuredTool.from_function(
    func=execute_step_function,
    name="execute_step", 
    description="Execute a single step from a plan. Use this to complete individual tasks from the plan created by the Planning Agent.",
    args_schema=ExecuteStepInput
)

