from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import logging
from app.utils.enterprise.handler_utils import process_zip
from fastapi import APIRouter
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ZIPProcessRequest(BaseModel):
    zip_path: str
    # output_dir: str = "output"  # Default output directory

@router.post("/process-zip/enterprise")
async def process_zip_file(request: ZIPProcessRequest):
    try:
        # Validate ZIP file path
        zip_path = Path(request.zip_path)
        if not zip_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"ZIP file not found at path: {zip_path}"
            )
        
        if not zip_path.suffix.lower() == '.zip':
            raise HTTPException(
                status_code=400,
                detail="File must be a ZIP archive"
            )
        
        # Create output directory if it doesn't exist
        print("Current directory:", Path.cwd())
        output_dir = Path.cwd() / "pdf_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process the ZIP file
        process_zip(
            zip_path=str(zip_path),
            output_dir=str(output_dir)
        )
        
        # Return the paths to the generated content
        markdown_path = output_dir / "markdown" / "content.md"
        images_dir = output_dir / "images"
        
        return {
            "status": "success",
            "message": "ZIP file processed successfully",
            "output_locations": {
                "markdown_file": str(markdown_path),
                "images_directory": str(images_dir),
                "output_directory": str(output_dir)
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing ZIP file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing ZIP file: {str(e)}"
        )