# app/main.py
from fastapi import FastAPI
import logging
from app.routers import pdf_extract_routes as pdf_routes
from app.routers import handler_routes
from app.routers import web_scraping_routes as web_routes


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
app.include_router(pdf_routes.router)
app.include_router(handler_routes.router)
app.include_router(web_routes.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "PDF Processing API",
        "version": "1.0.0",
         "endpoints": {
        "/extract-pdf/enterprise": "Extract content from PDF file using enterprise method",
          "/process-zip/enterprise": "Process ZIP file using enterprise method",
            "/web-scraping/enterprise": "Scrape content from website using enterprise method",
         "/web-scraping/opensource": "Scrape content from website using opensource method"
    }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)