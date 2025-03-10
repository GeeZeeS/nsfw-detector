import os
import sys
import subprocess
import importlib.util
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("nsfw-detector-install")

# Required packages
requirements = [
    "fastapi>=0.68.0",
    "python-multipart>=0.0.5",
    "python-magic>=0.4.24",
    "Pillow>=8.3.1",
    "python-docx>=0.8.11",
    "PyPDF2>=2.0.0",
    "opencv-python>=4.5.3",
    "numpy>=1.21.2",
    "transformers>=4.30.0",
    "torch>=2.0.0",
    "pdf2image>=1.16.3",
    "rarfile>=4.0",
]

# Windows-specific requirements
if sys.platform.startswith("win"):
    requirements.append("python-magic-bin>=0.4.14")

# Check if package is installed
def is_package_installed(package_name):
    try:
        spec = importlib.util.find_spec(package_name.split(">=")[0].split("==")[0])
        return spec is not None
    except (ImportError, ValueError, AttributeError):
        return False

# Install missing packages
def install_requirements():
    logger.info("Checking and installing required packages...")
    for req in requirements:
        package_name = req.split(">=")[0].split("==")[0]
        if not is_package_installed(package_name):
            logger.info(f"Installing {req}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", req])
                logger.info(f"Successfully installed {req}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {req}: {str(e)}")

# Main installation function
def install():
    try:
        logger.info("Starting NSFW Detector extension installation...")
        
        # Install package requirements
        install_requirements()
        
        # Create scripts directory if it doesn't exist
        scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        logger.info("NSFW Detector extension installed successfully!")
        logger.info("You can now use the NSFW detector from the Extensions tab in the UI.")
        logger.info("The API endpoint is available at /nsfw/check")
        
    except Exception as e:
        logger.error(f"Error installing NSFW Detector extension: {str(e)}")
        raise

if __name__ == "__main__":
    install() 