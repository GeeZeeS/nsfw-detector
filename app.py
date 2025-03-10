# app.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
import tempfile
import os
import shutil
import logging
import magic
import gc
from pathlib import Path
from typing import Optional, Dict, Any
from config import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, MIME_TO_EXT, DOCUMENT_EXTENSIONS
from utils import ArchiveHandler, can_process_file, sort_files_by_priority
from processors import (
    process_image, process_pdf_file, process_video_file, 
    process_archive, process_doc_file, process_docx_file
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router for Forge UI plugin
router = APIRouter(
    prefix="/api/nsfw",
    tags=["NSFW Detector"],
    responses={404: {"description": "Not found"}},
)

# Extension settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # Default 10MB

def get_extension_settings() -> Dict[str, Any]:
    """Get extension settings from Forge UI"""
    try:
        # In a real Forge UI environment, this would be provided by the platform
        settings = {
            "max_file_size": MAX_FILE_SIZE
        }
        return settings
    except Exception as e:
        logger.error(f"Failed to get extension settings: {str(e)}")
        return {"max_file_size": MAX_FILE_SIZE}

@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "NSFW Detector API",
        "version": "1.0.0",
        "endpoints": {
            "check": "/api/nsfw/check",
            "health": "/api/nsfw/health"
        }
    }

@router.post("/check")
async def check_file(
    request: Request,
    file: Optional[UploadFile] = File(None),
    path: Optional[str] = Form(None)
):
    """Unified file check endpoint for Forge UI"""
    # Verify Forge UI authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Invalid or missing authentication token')
    
    # Get extension settings
    settings = get_extension_settings()
    max_file_size = settings.get("max_file_size", MAX_FILE_SIZE)
    
    temp_handler = TempFileHandler()
    try:
        if path:
            # Handle file path
            abs_path = os.path.abspath(path)
            app_dir = os.path.abspath(os.path.dirname(__file__))
            
            # Security check: ensure path doesn't point to program directory
            if abs_path.startswith(app_dir):
                raise HTTPException(status_code=400, detail='Invalid path: cannot access program directory')
                
            # Check if file exists
            if not os.path.exists(abs_path):
                raise HTTPException(status_code=404, detail='File not found')
                
            # Check if it's a file
            if not os.path.isfile(abs_path):
                raise HTTPException(status_code=400, detail='Path is not a file')
                
            # Check file size
            file_size = os.path.getsize(abs_path)
            if file_size > max_file_size:
                raise HTTPException(status_code=400, detail='File too large')
                
            # Get original filename
            original_filename = os.path.basename(abs_path)
            
            # Detect file type
            detected_type = detect_file_type(abs_path)
            
            # Process file
            return process_file_by_type(abs_path, detected_type, original_filename, temp_handler)
            
        elif file:
            # Handle uploaded file
            if file.content_type and file.content_type not in MIME_TO_EXT:
                raise HTTPException(status_code=400, detail=f'Unsupported file type: {file.content_type}')
                
            # Create temporary file
            temp_file = temp_handler.create_temp_file()
            try:
                # Save uploaded file
                with open(temp_file.name, 'wb') as f:
                    content = await file.read()
                    if len(content) > max_file_size:
                        raise HTTPException(status_code=400, detail='File too large')
                    f.write(content)
                
                # Detect file type
                detected_type = detect_file_type(temp_file.name)
                
                # Process file
                return process_file_by_type(temp_file.name, detected_type, file.filename, temp_handler)
                
            finally:
                temp_handler.cleanup()
                
        else:
            raise HTTPException(status_code=400, detail='No file or path provided')
            
    except Exception as e:
        temp_handler.cleanup()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for Forge UI"""
    return {"status": "healthy"}

# This is the entry point that Forge UI will use to register the plugin
def register(app):
    """Register the plugin with Forge UI"""
    app.include_router(router)
    logger.info("NSFW Detector plugin registered successfully")