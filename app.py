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

class TempFileHandler:
    """Temporary file manager"""
    def __init__(self):
        self.temp_files = []
        self.temp_dirs = []
        
    def create_temp_file(self, suffix=None):
        """Create temporary file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        self.temp_files.append(temp_file.name)
        return temp_file
        
    def create_temp_dir(self):
        """Create temporary directory"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
        
    def cleanup(self):
        """Clean up all temporary files and directories"""
        # Clean up files
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f"Failed to clean up temporary file {file_path}: {str(e)}")
        self.temp_files.clear()
        
        # Clean up directories
        for dir_path in self.temp_dirs:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
            except Exception as e:
                logger.error(f"Failed to clean up temporary directory {dir_path}: {str(e)}")
        self.temp_dirs.clear()
        
        # Force garbage collection
        gc.collect()

def detect_file_type(file_path):
    """Detect file type using first 2048 bytes"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(2048)
        
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(header)
        
        # Special handling for RAR files
        if mime_type not in MIME_TO_EXT:
            with open(file_path, 'rb') as f:
                if f.read(7).startswith(b'Rar!\x1a\x07'):
                    return 'application/x-rar', '.rar'
        
        return mime_type, MIME_TO_EXT.get(mime_type)
        
    except Exception as e:
        logger.error(f"File type detection failed: {str(e)}")
        raise

def process_file_by_type(file_path, detected_type, original_filename, temp_handler):
    """Process file based on its type"""
    mime_type, ext = detected_type
    
    # Use original file extension if available
    if original_filename and '.' in original_filename:
        original_ext = os.path.splitext(original_filename)[1].lower()
        if original_ext in IMAGE_EXTENSIONS or original_ext == '.pdf' or \
           original_ext in VIDEO_EXTENSIONS or original_ext in {'.rar', '.zip', '.7z', '.gz'} or \
           original_ext in DOCUMENT_EXTENSIONS:
            ext = original_ext
    
    if not ext:
        logger.error(f"Unsupported file type: {mime_type}")
        raise HTTPException(status_code=400, detail=f'Unsupported file type: {mime_type}')
    
    try:
        if ext in IMAGE_EXTENSIONS:
            with open(file_path, 'rb') as f:
                from PIL import Image
                with Image.open(f) as image:
                    result = process_image(image)
                    gc.collect()
                    return {
                        'status': 'success',
                        'filename': original_filename,
                        'result': result
                    }
                
        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                pdf_stream = f.read()
                result = process_pdf_file(pdf_stream)
                gc.collect()
                if result:
                    return {
                        'status': 'success',
                        'filename': original_filename,
                        'result': result
                    }
                raise HTTPException(status_code=400, detail='No processable content found in PDF')
                
        elif ext in VIDEO_EXTENSIONS:
            result = process_video_file(file_path)
            gc.collect()
            if result:
                return {
                    'status': 'success',
                    'filename': original_filename,
                    'result': result
                }
            raise HTTPException(status_code=400, detail='No processable content found in video')
                
        elif ext in {'.zip', '.rar', '.7z', '.gz'}:
            result = process_archive(file_path, original_filename)
            gc.collect()
            return result
            
        elif ext in DOCUMENT_EXTENSIONS:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                if ext == '.doc':
                    result = process_doc_file(file_content)
                else:  # .docx
                    result = process_docx_file(file_content)
                
                gc.collect()
                    
                if result:
                    return {
                        'status': 'success',
                        'filename': original_filename,
                        'result': result
                    }
                raise HTTPException(status_code=400, detail='No processable content found in document')
            
        else:
            logger.error(f"Unsupported file extension: {ext}")
            raise HTTPException(status_code=400, detail=f'Unsupported file extension: {ext}')
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Create router for Forge UI plugin
router = APIRouter(
    prefix="/nsfw",
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
            "check": "/nsfw/check",
            "health": "/nsfw/health"
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