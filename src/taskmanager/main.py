import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from taskmanager.core import settings  
from taskmanager.controller import auth_router, task_router
from taskmanager.database import Base, engine
from taskmanager.model import User, Task

Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI(
    title=settings["APP_NAME"],
    description=settings["APP_DESCRIPTION"],
    version=settings["APP_VERSION"],
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings["FRONTEND_URL"]], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route controllers
app.include_router(auth_router)
app.include_router(task_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": settings["APP_NAME"],
        "status": "running",
        "version": settings["APP_VERSION"]
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run with uvicorn only when executed directly
if __name__ == "__main__":
    uvicorn.run(
        "taskmanager.main:app",  
        host=settings["HOST"],
        port=settings["PORT"],
        reload=settings["DEBUG"]
    )
