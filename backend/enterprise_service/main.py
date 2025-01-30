# app/main.py
from fastapi import FastAPI
import logging
from app.routes.pdf_routes import router as pdf_router
from app.routes.handler_routes import router as handler_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="PDF Processing API",
    description="API for processing PDF documents",
    version="1.0.0"
)

# Include routers
app.include_router(pdf_router)  # Changed from pdf_routes.router
app.include_router(handler_router)  # Changed from handler_routes.router

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "PDF Processing API",
        "version": "1.0.0",
        "endpoints": {
            "/extract-pdf/enterprise": "Extract content from PDF file using enterprise method",
            "/process-zip/enterprise": "Process ZIP file using enterprise method",
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)