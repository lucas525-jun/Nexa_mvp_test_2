import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.config import init_db, seed_sample_data
from app.routes import master_routes, order_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Nexa Task Manager - Test #2",
    description="Operational core MVP: Order management with master assignment and ADL enforcement",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed sample data on startup"""
    logger.info("Starting Nexa Task Manager API...")
    init_db()
    seed_sample_data()
    logger.info("Application started successfully")


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Nexa Task Manager API - Test #2", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "nexa-task-manager-test2", "version": "1.0.0"}


# Include routers
app.include_router(order_routes.router, prefix="/api/v1")
app.include_router(master_routes.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
