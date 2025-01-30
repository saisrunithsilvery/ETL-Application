import os
from fastapi import FastAPI, HTTPException
from fastapi import APIRouter

from pydantic import BaseModel
from pathlib import Path
import logging

from app.utils.enterprise.jina import extract_images_from_html,fetch_html,replace_html

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class PDFExtractionRequest(BaseModel):
    url: str
    output_dir: str

@router.post("/web-Scraping/enterprise")
async def extract_pdf(request: PDFExtractionRequest):
    try:
        # Validate paths
        url = Path(request.url)
        output_dir = Path(request.output_dir)
        
        # Check if PDF file exists
        if not url.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Web page not found : {url}"
            )
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        #Web scraping extraction:
        api_key = os.getenv("JINA_API_KEY")
        html_path, html_content = fetch_html(url, output_dir, api_key)

        # Step 2: Extract images from HTML
        extract_images_from_html(html_content, output_dir, url)
        replace_html(html_content,output_dir)


        
        
        return {
            "status": "success",
            "saved path": html_path,
            "message": "PDF extraction completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

            
__all__ = ['router'] 