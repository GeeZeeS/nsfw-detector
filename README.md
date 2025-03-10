# NSFW Detector for Automatic1111 Web UI

A powerful NSFW content detection extension for Automatic1111 Stable Diffusion Web UI that can analyze images for NSFW content.

## Features

- Detect NSFW content in images
- Block NSFW generated images automatically
- Configure detection threshold 
- Simple UI in the Extensions tab
- API endpoint for external applications
- High accuracy using state-of-the-art AI models

## Installation

### Method 1: Install from Extensions Tab

1. Open Automatic1111 Web UI
2. Go to the "Extensions" tab
3. Click on "Install from URL"
4. Paste this repo URL: `https://github.com/yourusername/nsfw-detector.git`
5. Click "Install"
6. Restart the Web UI

### Method 2: Manual Installation

1. Navigate to your Automatic1111 extensions folder:
   ```bash
   cd /path/to/stable-diffusion-webui/extensions/
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/nsfw-detector.git
   ```

3. Restart the Web UI

## Usage

### UI Interface

After installation, you'll find a new tab called "NSFW Detector" in the Web UI. Here you can:

1. Set the NSFW detection threshold (default: 0.8)
2. Enable/disable checking of generated images
3. Enable/disable automatic blocking of NSFW images
4. Test detection on your own images

### API Usage

The extension adds a new API endpoint at `/nsfw/check`. You can use it like this:

```python
import requests

# Check an image
files = {'image': open('image.jpg', 'rb')}
response = requests.post('http://localhost:7860/nsfw/check', files=files)
print(response.json())
```

The API returns JSON responses in the following format:

```json
{
    "status": "success",
    "filename": "example.jpg",
    "result": {
        "nsfw": 0.95,
        "normal": 0.05
    },
    "is_nsfw": true
}
```

## Configuration

All settings can be changed through the NSFW Detector tab in the Web UI:

- **NSFW Detection Threshold**: The confidence threshold above which an image is considered NSFW (default: 0.8)
- **Check Generated Images**: If enabled, all generated images will be checked for NSFW content
- **Block NSFW Images**: If enabled, images detected as NSFW will be blocked from the results

## System Requirements

- Automatic1111 Web UI
- Python 3.8 or higher
- Enough VRAM to run both Stable Diffusion and the NSFW detection model

## License

MIT License - see LICENSE file for details. 