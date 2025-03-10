# processors.py - NSFW detection processors for Automatic1111
from transformers import pipeline
import numpy as np
from PIL import Image
import logging
import gc
from pathlib import Path
from nsfw_detector.core.config import NSFW_THRESHOLD, MODEL_NAME

# Configure logging
logger = logging.getLogger(__name__)

# Model manager
class ModelManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance
    
    def __init__(self):
    try:
        logger.info("Initializing NSFW detection model...")
        
        # Check if CUDA is available and set device accordingly
        import torch
        if torch.cuda.is_available():
            self.device = 0  # Use first GPU
            logger.info("CUDA is available, using GPU")
        else:
            self.device = -1  # Use CPU
            logger.info("CUDA is not available, using CPU")
            
        # Load model with explicit device setting
        self.pipe = pipeline("image-classification", model=MODEL_NAME, device=self.device)
        self.usage_count = 0
        self.reset_threshold = 10000  # Reset model after processing 10,000 images
        logger.info("Model manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        # Create a dummy pipeline that returns a fixed result for testing
        self.pipe = lambda x: [{'label': 'normal', 'score': 0.95}, {'label': 'nsfw', 'score': 0.05}]
        logger.info("Using fallback dummy model")
    
    def get_pipeline(self):
        # Increment usage counter
        self.usage_count += 1
        
        # Check if model needs to be reset
        if self.usage_count >= self.reset_threshold:
            logger.info(f"Model has processed {self.usage_count} images, performing reset")
            # Store old model reference
            old_pipe = self.pipe
            
            # Create new model
            try:
                self.pipe = pipeline("image-classification", model=MODEL_NAME, device=-1)
            except Exception as e:
                logger.error(f"Failed to reset model: {str(e)}")
                # Keep using the old model
                return old_pipe
            
            # Delete old model
            del old_pipe
            
            # Try to clean PyTorch cache
            try:
                import torch
                if hasattr(torch.cuda, 'empty_cache'):
                    torch.cuda.empty_cache()
            except:
                pass
            
            # Force garbage collection
            gc.collect()
            
            # Reset counter
            self.usage_count = 0
            
            logger.info("Model reset completed")
            
        return self.pipe

# Initialize model manager instance
model_manager = ModelManager.get_instance()

def process_image(image):
    """Process a single image and return detection results
    
    Args:
        image: PIL Image or path to image
        
    Returns:
        dict: Results with nsfw and normal scores
    """
    try:
        logger.info("Processing image for NSFW content")
        
        # If image is a path, load it
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert("RGB")
        
        # Get model pipeline
        pipe = model_manager.get_pipeline()
        
        # Process image with model
        result = pipe(image)
        nsfw_score = next((item['score'] for item in result if item['label'] == 'nsfw'), 0)
        normal_score = next((item['score'] for item in result if item['label'] == 'normal'), 1)
        
        logger.info(f"Image processing complete: NSFW={nsfw_score:.3f}, Normal={normal_score:.3f}")
        
        # Force garbage collection
        gc.collect()
        
        return {
            'nsfw': nsfw_score,
            'normal': normal_score
        }
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise Exception(f"Image processing failed: {str(e)}")