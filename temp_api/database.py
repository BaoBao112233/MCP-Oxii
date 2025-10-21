from typing import Dict, List, Optional
from models import PlanDB, TaskDB, PlanCreate, TaskCreate, TaskUpdate, PlanUpdate
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class InMemoryDatabase:
    def __init__(self):
        self.plans: Dict[str, PlanDB] = {}
        self.tasks: Dict[str, TaskDB] = {}

    def create_plan(self, plan_data: PlanCreate) -> PlanDB:
        """Create a new plan with tasks"""
        plan = PlanDB(
            session_id=plan_data.session_id,
            title=plan_data.title,
            goal_text=plan_data.goal_text,
            trigger=plan_data.trigger,
            priority=plan_data.priority
        )

        logger.debug(f"Creating plan: {plan.id}")
        # Create tasks for this plan
        tasks = []
        for task_data in plan_data.tasks:
            task = TaskDB(
                plan_id=plan.id,
                order_no=task_data.order_no,
                title=task_data.title,
                description=task_data.description,
                max_retries=task_data.max_retries
            )
            tasks.append(task)
            self.tasks[task.id] = task
            logger.debug(f"Created task: {task.id} for plan: {plan.id}")
        plan.tasks = tasks
        logger.debug(f"Total tasks created for plan {plan.id}: {len(tasks)}")
        self.plans[plan.id] = plan
        return plan

    def create_plans(self, plans_data: List[PlanCreate]) -> List[PlanDB]:
        """Create multiple plans"""
        logger.debug(f"Creating multiple plans: {len(plans_data)} plans to create")
        created_plans = []
        for plan_data in plans_data:
            plan = self.create_plan(plan_data)
            created_plans.append(plan)
        logger.debug(f"Total plans created: {len(created_plans)}")
        return created_plans

    def get_plan(self, plan_id: str) -> Optional[PlanDB]:
        """Get a plan by ID"""
        logger.debug(f"Retrieving plan: {plan_id}")
        return self.plans.get(plan_id)

    def get_task(self, task_id: str) -> Optional[TaskDB]:
        """Get a task by ID"""
        logger.debug(f"Retrieving task: {task_id}")
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, updates: TaskUpdate) -> Optional[TaskDB]:
        """Update a task"""
        task = self.tasks.get(task_id)
        if not task:
            logger.warning(f"Task not found: {task_id}")
            return None

        if updates.status is not None:
            logger.debug(f"Updating task status: {task_id} to {updates.status}")
            task.status = updates.status
        if updates.execution_result is not None:
            logger.debug(f"Updating task execution result: {task_id}")
            task.execution_result = updates.execution_result

        logger.debug(f"Task updated: {task_id}")
        task.updated_at = datetime.now()
        return task

    def update_plan(self, plan_id: str, updates: PlanUpdate) -> Optional[PlanDB]:
        """Update a plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            logger.warning(f"Plan not found: {plan_id}")
            return None

        if updates.status is not None:
            logger.debug(f"Updating plan status: {plan_id} to {updates.status}")
            plan.status = updates.status
        if updates.goal_text is not None:
            logger.debug(f"Updating plan goal text: {plan_id}")
            plan.goal_text = updates.goal_text

        logger.debug(f"Plan updated: {plan_id}")
        plan.updated_at = datetime.now()
        return plan

    def get_all_plans(self) -> List[PlanDB]:
        """Get all plans"""
        logger.debug(f"Retrieving all plans")
        return list(self.plans.values())

    def get_tasks_by_plan(self, plan_id: str) -> List[TaskDB]:
        """Get all tasks for a specific plan"""
        logger.debug(f"Retrieving tasks for plan: {plan_id}")
        return [task for task in self.tasks.values() if task.plan_id == plan_id]


# Global database instance
db = InMemoryDatabase()