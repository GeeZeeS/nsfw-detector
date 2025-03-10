# config.py - Configuration for NSFW detector
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# MIME type to file extension mapping for supported formats
MIME_TO_EXT = {
    # Image formats
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp',
    'image/bmp': '.bmp',
    'image/tiff': '.tiff',
    'image/x-tiff': '.tiff'
}

# File extension sets
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

# Default configuration values
NSFW_THRESHOLD = 0.8
MODEL_NAME = "Falconsai/nsfw_image_detection"

# Export all configuration variables
__all__ = [
    'MIME_TO_EXT', 'IMAGE_EXTENSIONS', 'NSFW_THRESHOLD', 'MODEL_NAME'
]