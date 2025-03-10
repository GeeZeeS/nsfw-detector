# config.py
import os
import rarfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def load_forge_config():
    """Load configuration from Forge UI environment variables"""
    config = {}
    env_prefix = "FORGE_CONFIG_"
    
    # Map environment variables to config
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            config_key = key[len(env_prefix):]
            try:
                # Try to convert to appropriate type
                if value.lower() in ('true', 'false'):
                    config[config_key] = value.lower() == 'true'
                elif '.' in value:
                    config[config_key] = float(value)
                else:
                    config[config_key] = int(value)
            except ValueError:
                config[config_key] = value
                
    return config

# Base configuration
rarfile.UNRAR_TOOL = "unrar"
rarfile.PATH_SEP = '/'
os.environ['HF_HOME'] = os.path.expanduser('~/.cache/huggingface')

# MIME type to file extension mapping
MIME_TO_EXT = {
    # Image formats
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp',
    'image/bmp': '.bmp',
    'image/tiff': '.tiff',
    'image/x-tiff': '.tiff',
    'image/x-tga': '.tga',
    'image/x-portable-pixmap': '.ppm',
    'image/x-portable-graymap': '.pgm',
    'image/x-portable-bitmap': '.pbm',
    'image/x-portable-anymap': '.pnm',
    'image/svg+xml': '.svg',
    'image/x-pcx': '.pcx',
    'image/vnd.adobe.photoshop': '.psd',
    'image/vnd.microsoft.icon': '.ico',
    'image/heif': '.heif',
    'image/heic': '.heic',
    'image/avif': '.avif',
    'image/jxl': '.jxl',
    
    # PDF format
    'application/pdf': '.pdf',
    
    # Document formats
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    
    # Video formats
    'video/mp4': '.mp4',
    'video/x-msvideo': '.avi',
    'video/x-matroska': '.mkv',
    'video/quicktime': '.mov',
    'video/x-ms-wmv': '.wmv',
    'video/webm': '.webm',
    'video/MP2T': '.ts',    
    'video/x-flv': '.flv',
    'video/3gpp': '.3gp',
    'video/3gpp2': '.3g2',
    'video/x-m4v': '.m4v',
    'video/mxf': '.mxf',
    'video/x-ogm': '.ogm',
    'video/vnd.rn-realvideo': '.rv',
    'video/dv': '.dv',
    'video/x-ms-asf': '.asf',
    'video/x-f4v': '.f4v',
    'video/vnd.dlna.mpeg-tts': '.m2ts',
    'video/x-raw': '.yuv',
    'video/mpeg': '.mpg',
    'video/x-mpeg': '.mpeg',
    'video/divx': '.divx',
    'video/x-vob': '.vob',
    'video/x-m2v': '.m2v',
    
    # Archive formats
    'application/x-rar-compressed': '.rar',
    'application/x-rar': '.rar',
    'application/vnd.rar': '.rar',
    'application/zip': '.zip',
    'application/x-7z-compressed': '.7z',
    'application/gzip': '.gz',
    'application/x-tar': '.tar',
    'application/x-bzip2': '.bz2',
    'application/x-xz': '.xz',
    'application/x-lzma': '.lzma',
    'application/x-zstd': '.zst',
    'application/vnd.ms-cab-compressed': '.cab'
}

# File extension sets
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tga', 
                   '.ppm', '.pgm', '.pbm', '.pnm', '.svg', '.pcx', '.psd', '.ico',
                   '.heif', '.heic', '.avif', '.jxl'}

VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm', '.ts', '.flv',
                   '.3gp', '.3g2', '.m4v', '.mxf', '.ogm', '.rv', '.dv', '.asf',
                   '.f4v', '.m2ts', '.yuv', '.mpg', '.mpeg', '.divx', '.vob', '.m2v'}

ARCHIVE_EXTENSIONS = {'.7z', '.rar', '.zip', '.gz', '.tar', '.bz2', '.xz', 
                     '.lzma', '.zst', '.cab'}

DOCUMENT_EXTENSIONS = {'.doc', '.docx'}

# MIME type sets
DOCUMENT_MIME_TYPES = {
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

IMAGE_MIME_TYPES = {mime for mime, ext in MIME_TO_EXT.items() if mime.startswith('image/')}
VIDEO_MIME_TYPES = {mime for mime, ext in MIME_TO_EXT.items() if mime.startswith('video/')}
ARCHIVE_MIME_TYPES = {mime for mime, ext in MIME_TO_EXT.items() if 
    mime.startswith('application/') and 
    any(keyword in mime for keyword in ['zip', 'rar', '7z', 'gzip', 'tar', 
        'bzip2', 'xz', 'lzma', 'zstd', 'cab'])}
PDF_MIME_TYPES = {'application/pdf'}

# All supported MIME types
SUPPORTED_MIME_TYPES = IMAGE_MIME_TYPES | VIDEO_MIME_TYPES | ARCHIVE_MIME_TYPES | PDF_MIME_TYPES | DOCUMENT_MIME_TYPES

# Default configuration values
MAX_FILE_SIZE = 20 * 1024 * 1024 * 1024  # 20GB
NSFW_THRESHOLD = 0.8
FFMPEG_MAX_FRAMES = 20
FFMPEG_TIMEOUT = 1800
CHECK_ALL_FILES = False
MAX_INTERVAL_SECONDS = 30

# Load configuration from Forge UI and update globals
forge_config = load_forge_config()
globals().update(forge_config)

# Export all configuration variables
__all__ = [
    'MIME_TO_EXT', 'IMAGE_EXTENSIONS', 'VIDEO_EXTENSIONS', 'ARCHIVE_EXTENSIONS',
    'DOCUMENT_EXTENSIONS',
    'IMAGE_MIME_TYPES', 'VIDEO_MIME_TYPES', 'ARCHIVE_MIME_TYPES', 'PDF_MIME_TYPES',
    'DOCUMENT_MIME_TYPES',
    'SUPPORTED_MIME_TYPES', 'MAX_FILE_SIZE', 'NSFW_THRESHOLD', 'FFMPEG_MAX_FRAMES', 
    'FFMPEG_TIMEOUT', 'CHECK_ALL_FILES', 'MAX_INTERVAL_SECONDS'
]