from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.plans import router as plans_router

# Create FastAPI app
app = FastAPI(
    title="Planner API",
    description="API for managing plans and tasks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    plans_router,
    prefix="/api/v1",
    tags=["plans"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Planner API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)