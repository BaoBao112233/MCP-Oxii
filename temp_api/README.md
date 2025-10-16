# Planner API

FastAPI application for managing plans and tasks with GraphQL-like response format.

## Features

- ✅ Create multiple plans with tasks
- ✅ Update plan status and goal text
- ✅ Update task status and execution results
- ✅ Get plans and tasks
- ✅ In-memory storage (for development/demo)

## Installation

```bash
cd temp_api
pip install -r requirements.txt
```

## Running the API

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Create Plans
```http
POST /api/v1/plans
Content-Type: application/json

[
  {
    "session_id": 1,
    "title": "Plan A – Mức độ đề xuất: Cao",
    "goal_text": "mục đích",
    "trigger": "SYSTEM",
    "priority": 1,
    "tasks": [
      {
        "order_no": 1,
        "title": "Bật đèn phòng khách",
        "description": "Mô tả task 1",
        "max_retries": 2
      }
    ]
  }
]
```

### Update Plan
```http
PUT /api/v1/plans/{plan_id}
Content-Type: application/json

{
  "status": "completed",
  "goal_text": "Updated goal"
}
```

### Update Task
```http
PUT /api/v1/tasks/{task_id}
Content-Type: application/json

{
  "status": "completed",
  "execution_result": "Task executed successfully"
}
```

### Get All Plans
```http
GET /api/v1/plans
```

### Get Specific Plan
```http
GET /api/v1/plans/{plan_id}
```

### Get Specific Task
```http
GET /api/v1/tasks/{task_id}
```

## Response Format

The API returns responses in a format similar to GraphQL mutations:

```json
{
  "data": {
    "insert_planner_plans": {
      "affected_rows": 2,
      "returning": [
        {
          "id": "uuid",
          "title": "Plan Title",
          "goal_text": "Goal description",
          "trigger": "SYSTEM",
          "priority": 1,
          "status": "created",
          "created_at": "2025-10-16T10:00:00",
          "updated_at": "2025-10-16T10:00:00",
          "tasks": [
            {
              "id": "uuid",
              "order_no": 1,
              "title": "Task Title",
              "description": "Task description",
              "max_retries": 2,
              "status": "pending",
              "execution_result": null,
              "created_at": "2025-10-16T10:00:00",
              "updated_at": "2025-10-16T10:00:00"
            }
          ]
        }
      ]
    }
  }
}
```

## Testing

You can test the API using the interactive Swagger UI at: http://localhost:8000/docs

Or run the test script:

```bash
cd temp_api
python test_api.py
```

Or use curl:

```bash
# Create plans
curl -X POST "http://localhost:8000/api/v1/plans" \
     -H "Content-Type: application/json" \
     -d @test_plans.json

# Get all plans
curl -X GET "http://localhost:8000/api/v1/plans"
```