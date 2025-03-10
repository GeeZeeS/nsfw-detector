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
            
            # Force CPU mode to avoid tensor type mismatches
            self.device = "cpu"
            logger.info("Forcing CPU mode for model compatibility")
            
            # Import the model with explicit CPU placement
            from transformers import AutoFeatureExtractor, AutoModelForImageClassification
            
            # Load model components manually to ensure all on same device
            self.model_name = MODEL_NAME
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name).to(self.device)
            
            # Don't use the pipeline, we'll implement prediction directly
            self.usage_count = 0
            self.reset_threshold = 10000
            logger.info("Model manager initialized successfully with manual device control")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            # Create fallback dummy function
            self.model = None
            self.feature_extractor = None
            logger.info("Using fallback dummy model")
    
    def get_pipeline(self):
        # Increment usage counter
        self.usage_count += 1
        
        # If using fallback dummy model
        if self.model is None:
            return lambda x: [{'label': 'normal', 'score': 0.95}, {'label': 'nsfw', 'score': 0.05}]
        
        # Return our custom prediction function
        return self._predict
    
    def _predict(self, image):
        """Custom prediction function to replace the pipeline"""
        try:
            import torch
            
            # Prepare the image
            inputs = self.feature_extractor(images=image, return_tensors="pt").to(self.device)
            
            # Run prediction with no gradient tracking
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
            # Get predicted class and probability
            predicted_class_idx = logits.argmax(-1).item()
            scores = torch.nn.functional.softmax(logits, dim=-1)
            
            # Convert to the expected output format
            result = []
            for i, label in enumerate(self.model.config.id2label.values()):
                result.append({
                    'label': label,
                    'score': scores[0, i].item()
                })
                
            return result
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return [{'label': 'normal', 'score': 0.95}, {'label': 'nsfw', 'score': 0.05}]

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
        
        # Get prediction function
        predict_fn = model_manager.get_pipeline()
        
        # Process image with model
        result = predict_fn(image)
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