import os
import logging
import torch
import gradio as gr
from modules import scripts, shared, script_callbacks
from modules.processing import process_images, Processed
from nsfw_detector.services.processors import process_image
import scripts.nsfw_detector as nsfw_detector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class NSFWDetectorScript(scripts.Script):
    def __init__(self):
        super().__init__()
        self.blocked_count = 0
        self.checked_count = 0
    
    def title(self):
        return "NSFW Detector"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def ui(self, is_img2img):
        # No UI elements needed here as they're in the extension tab
        return []
    
    def postprocess_image(self, p, processed, *args):
        """Check generated images for NSFW content"""
        # Skip if checking is disabled
        if not nsfw_detector.nsfw_config["check_generated_images"]:
            return processed
        
        # Get threshold from config
        threshold = nsfw_detector.nsfw_config["threshold"]
        block_nsfw = nsfw_detector.nsfw_config["block_nsfw_images"]
        
        # Process each image
        filtered_images = []
        filtered_info_texts = []
        blocked_any = False
        
        for i, image in enumerate(processed.images):
            self.checked_count += 1
            try:
                # Process the image for NSFW content
                results = process_image(image)
                nsfw_score = results.get('nsfw', 0)
                normal_score = results.get('normal', 0)
                is_nsfw = nsfw_score > threshold
                
                # Add NSFW score to info text
                if i < len(processed.infotexts):
                    processed.infotexts[i] += f"\nNSFW Score: {nsfw_score:.4f}"
                
                # If image is NSFW and blocking is enabled, skip it
                if is_nsfw and block_nsfw:
                    logger.info(f"Blocking NSFW image with score {nsfw_score:.4f}")
                    self.blocked_count += 1
                    blocked_any = True
                    continue
                
                # Keep the image
                filtered_images.append(image)
                if i < len(processed.infotexts):
                    filtered_info_texts.append(processed.infotexts[i])
                
            except Exception as e:
                logger.error(f"Error checking image for NSFW content: {str(e)}")
                # Keep the image if there's an error
                filtered_images.append(image)
                if i < len(processed.infotexts):
                    filtered_info_texts.append(processed.infotexts[i])
        
        # If any images were blocked, update the processed object
        if blocked_any:
            processed.images = filtered_images
            processed.infotexts = filtered_info_texts
            
            # Add a message to the info
            blocked_msg = f"⚠️ {self.blocked_count} NSFW images blocked by NSFW Detector"
            if hasattr(processed, 'info') and processed.info is not None:
                processed.info += f"\n\n{blocked_msg}"
            else:
                processed.info = blocked_msg
        
        return processed 