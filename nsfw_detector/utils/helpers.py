# helpers.py - Utility functions for NSFW detector
import os
import logging
from pathlib import Path
from nsfw_detector.core.config import IMAGE_EXTENSIONS

# Configure logging
logger = logging.getLogger(__name__)

def get_file_extension(filename):
    """Get the file extension from a filename"""
    ext = os.path.splitext(filename)[1].lower()
    return ext

def is_image_file(filename):
    """Check if a file is an image based on its extension"""
    ext = get_file_extension(filename)
    return ext in IMAGE_EXTENSIONS

def get_mime_type(file_path):
    """Get the MIME type of a file"""
    try:
        import magic
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except ImportError:
        logger.warning("python-magic not installed, using basic type detection")
        ext = get_file_extension(file_path)
        if ext in {'.jpg', '.jpeg'}:
            return 'image/jpeg'
        elif ext == '.png':
            return 'image/png'
        elif ext == '.gif':
            return 'image/gif'
        elif ext == '.webp':
            return 'image/webp'
        elif ext == '.bmp':
            return 'image/bmp'
        elif ext in {'.tiff', '.tif'}:
            return 'image/tiff'
        else:
            return 'application/octet-stream'