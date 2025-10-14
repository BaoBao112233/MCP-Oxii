from fastapi import FastAPI
import uvicorn
import os

from template.configs.environment import get_environment_variables
from template.routers.v1.ai import AgentRouter


# Application Environment Configuration
env = get_environment_variables()

# Core Application Instance
app = FastAPI(
    title=env.APP_NAME,
    version=env.API_VERSION
)

# Add Routers
app.include_router(AgentRouter)

# Health check endpoint for Docker
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    # Get port from environment or default to 7000
    # Get port from the environment or default to 7000
    port = int(os.environ.get("PORT", env.APP_PORT))
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=port)