# NSFW Detector for Forge UI

A powerful NSFW content detection plugin for Forge UI that can analyze images, videos, PDFs, and documents.

## Features

- Detect NSFW content in multiple file formats:
  - Images (JPG, PNG, GIF, WebP, etc.)
  - Videos (MP4, AVI, MKV, etc.)
  - Documents (PDF, DOC, DOCX)
  - Archives (ZIP, RAR, 7Z, etc.)
- High accuracy using state-of-the-art AI models
- Fast processing with optimized performance
- Support for nested archives
- Comprehensive MIME type detection

## Installation

To install the NSFW Detector plugin in your Forge UI environment:

```bash
pip install git+https://github.com/yourusername/nsfw-detector.git
```

Or add to your project's requirements.txt:

```
git+https://github.com/yourusername/nsfw-detector.git
```

### System Requirements

- Python 3.8 or higher
- For video processing: ffmpeg
- For archive handling: 
  - unrar (for RAR files)
  - p7zip (for 7z files)
  - antiword (for DOC files)

On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install ffmpeg unrar p7zip-full antiword
```

On macOS:
```bash
brew install ffmpeg unrar p7zip antiword
```

## Usage

The plugin will be automatically registered with Forge UI upon installation. You can access it through the `/nsfw/check` endpoint:

```python
import requests

# Check a file
files = {'file': open('image.jpg', 'rb')}
response = requests.post('http://your-forge-ui/nsfw/check', files=files)
print(response.json())

# Check a file by path
data = {'path': '/path/to/file.jpg'}
response = requests.post('http://your-forge-ui/nsfw/check', data=data)
print(response.json())
```

## Response Format

The API returns JSON responses in the following format:

```json
{
    "status": "success",
    "filename": "example.jpg",
    "result": {
        "nsfw": 0.95,
        "normal": 0.05
    }
}
```

For archives, it includes the matched file information:

```json
{
    "status": "success",
    "filename": "archive.zip",
    "matched_file": "subfolder/image.jpg",
    "result": {
        "nsfw": 0.95,
        "normal": 0.05
    }
}
```

## Configuration

The plugin can be configured through environment variables:

- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 20GB)
- `NSFW_THRESHOLD`: Threshold for NSFW detection (default: 0.8)
- `FFMPEG_MAX_FRAMES`: Maximum frames to extract from videos (default: 20)
- `FFMPEG_TIMEOUT`: Timeout for video processing in seconds (default: 1800)
- `CHECK_ALL_FILES`: Whether to check all files in archives (default: 0)
- `MAX_INTERVAL_SECONDS`: Maximum interval between frame extractions (default: 30)

## License

MIT License - see LICENSE file for details. 