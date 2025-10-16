from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from models import (
    PlanCreate, PlanUpdate, TaskUpdate,
    PlanResponse, TaskResponse, InsertPlansResponse, ApiResponse
)
from database import db

router = APIRouter()


@router.post("/plans", response_model=ApiResponse)
async def create_plans(plans: List[PlanCreate]) -> ApiResponse:
    """
    Create multiple plans with their tasks.
    Returns response in the format similar to GraphQL mutation.
    """
    try:
        created_plans = db.create_plans(plans)

        # Convert to response format
        returning = []
        for plan in created_plans:
            tasks_response = [
                TaskResponse(
                    id=task.id,
                    order_no=task.order_no,
                    title=task.title,
                    description=task.description,
                    max_retries=task.max_retries,
                    status=task.status,
                    execution_result=task.execution_result,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
                for task in plan.tasks
            ]

            plan_response = PlanResponse(
                id=plan.id,
                title=plan.title,
                goal_text=plan.goal_text,
                trigger=plan.trigger,
                priority=plan.priority,
                status=plan.status,
                created_at=plan.created_at,
                updated_at=plan.updated_at,
                tasks=tasks_response
            )
            returning.append(plan_response)

        response_data = {
            "insert_planner_plans": InsertPlansResponse(
                affected_rows=len(created_plans),
                returning=returning
            )
        }

        return ApiResponse(data=response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plans: {str(e)}")


@router.put("/plans/{plan_id}", response_model=Dict[str, Any])
async def update_plan(plan_id: str, updates: PlanUpdate) -> Dict[str, Any]:
    """
    Update a plan's status or goal_text.
    """
    plan = db.update_plan(plan_id, updates)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "success": True,
        "data": {
            "id": plan.id,
            "title": plan.title,
            "goal_text": plan.goal_text,
            "status": plan.status,
            "updated_at": plan.updated_at
        }
    }


@router.put("/tasks/{task_id}", response_model=Dict[str, Any])
async def update_task(task_id: str, updates: TaskUpdate) -> Dict[str, Any]:
    """
    Update a task's status and/or execution result.
    """
    task = db.update_task(task_id, updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "success": True,
        "data": {
            "id": task.id,
            "order_no": task.order_no,
            "title": task.title,
            "status": task.status,
            "execution_result": task.execution_result,
            "updated_at": task.updated_at
        }
    }


@router.get("/plans", response_model=List[PlanResponse])
async def get_all_plans() -> List[PlanResponse]:
    """
    Get all plans with their tasks.
    """
    plans = db.get_all_plans()
    response = []

    for plan in plans:
        tasks_response = [
            TaskResponse(
                id=task.id,
                order_no=task.order_no,
                title=task.title,
                description=task.description,
                max_retries=task.max_retries,
                status=task.status,
                execution_result=task.execution_result,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in plan.tasks
        ]

        plan_response = PlanResponse(
            id=plan.id,
            title=plan.title,
            goal_text=plan.goal_text,
            trigger=plan.trigger,
            priority=plan.priority,
            status=plan.status,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            tasks=tasks_response
        )
        response.append(plan_response)

    return response


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str) -> PlanResponse:
    """
    Get a specific plan with its tasks.
    """
    plan = db.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    tasks_response = [
        TaskResponse(
            id=task.id,
            order_no=task.order_no,
            title=task.title,
            description=task.description,
            max_retries=task.max_retries,
            status=task.status,
            execution_result=task.execution_result,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in plan.tasks
    ]

    return PlanResponse(
        id=plan.id,
        title=plan.title,
        goal_text=plan.goal_text,
        trigger=plan.trigger,
        priority=plan.priority,
        status=plan.status,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        tasks=tasks_response
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """
    Get a specific task.
    """
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        id=task.id,
        order_no=task.order_no,
        title=task.title,
        description=task.description,
        max_retries=task.max_retries,
        status=task.status,
        execution_result=task.execution_result,
        created_at=task.created_at,
        updated_at=task.updated_at
    )