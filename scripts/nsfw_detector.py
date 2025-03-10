import os
import sys
import gradio as gr
import time
import logging
import torch
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from modules import scripts, script_callbacks, shared
from modules.api.api import Api
from nsfw_detector.services.processors import process_image
from PIL import Image
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Store configuration in a dict to make it accessible via UI
nsfw_config = {
    "threshold": 0.8,
    "check_generated_images": False,
    "block_nsfw_images": False,
}

def on_app_started(demo: gr.Blocks, app: FastAPI):
    """This function is called when the Gradio app starts."""
    logger.info("Initializing NSFW Detector extension for Automatic1111")
    
    # Create a new API instance
    nsfw_api = Api(app, queue_lock=None)
    
    @app.post("/nsfw/check", tags=["NSFW Detector"])
    async def check_nsfw(
        image: UploadFile = File(..., description="Image to check for NSFW content"),
    ):
        """Check if an image contains NSFW content.
        
        Args:
            image: The image to check.
            
        Returns:
            JSON response with NSFW detection results.
        """
        try:
            logger.info(f"Received NSFW check request for image: {image.filename}")
            
            # Read the image data
            contents = await image.read()
            pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
            
            # Process the image
            results = process_image(pil_image)
            
            # Determine if the image is NSFW based on threshold
            is_nsfw = results.get('nsfw', 0) > nsfw_config["threshold"]
            
            return JSONResponse({
                "status": "success",
                "filename": image.filename,
                "result": results,
                "is_nsfw": is_nsfw
            })
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return JSONResponse({
                "status": "error",
                "message": str(e)
            }, status_code=500)
    
    logger.info("NSFW Detector API endpoint registered at /nsfw/check")


# This creates the UI components for the extension
def on_ui_tabs():
    """Create UI elements for the extension."""
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            with gr.Column():
                gr.Markdown("## NSFW Detector Settings")
                
                with gr.Row():
                    nsfw_threshold = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        step=0.05,
                        value=nsfw_config["threshold"],
                        label="NSFW Detection Threshold"
                    )
                
                with gr.Row():
                    check_generated = gr.Checkbox(
                        value=nsfw_config["check_generated_images"],
                        label="Check Generated Images"
                    )
                
                with gr.Row():
                    block_nsfw = gr.Checkbox(
                        value=nsfw_config["block_nsfw_images"],
                        label="Block NSFW Images"
                    )
                
                with gr.Row():
                    save_button = gr.Button("Save Settings")
                
                with gr.Row():
                    result_text = gr.Markdown("Settings will be applied after saving.")
            
            with gr.Column():
                gr.Markdown("## Test NSFW Detection")
                
                with gr.Row():
                    test_image = gr.Image(label="Upload Image to Test", type="pil")
                
                with gr.Row():
                    test_button = gr.Button("Test Detection")
                
                with gr.Row():
                    test_result = gr.JSON(label="Detection Result")
        
        # Handle setting changes
        def save_settings(threshold, check_generated, block_nsfw):
            nsfw_config["threshold"] = threshold
            nsfw_config["check_generated_images"] = check_generated
            nsfw_config["block_nsfw_images"] = block_nsfw
            return "Settings saved successfully."
        
        save_button.click(
            fn=save_settings,
            inputs=[nsfw_threshold, check_generated, block_nsfw],
            outputs=[result_text]
        )
        
        # Handle test button
        def test_detection(image):
            if image is None:
                return {"error": "No image provided"}
            
            try:
                results = process_image(image)
                is_nsfw = results.get('nsfw', 0) > nsfw_config["threshold"]
                
                return {
                    "is_nsfw": is_nsfw,
                    "nsfw_score": results.get('nsfw', 0),
                    "normal_score": results.get('normal', 0),
                    "threshold": nsfw_config["threshold"]
                }
            except Exception as e:
                return {"error": str(e)}
        
        test_button.click(
            fn=test_detection,
            inputs=[test_image],
            outputs=[test_result]
        )
        
        return [(ui_component, "NSFW Detector", "nsfw_detector")]


# Register callbacks with Automatic1111
script_callbacks.on_app_started(on_app_started)
script_callbacks.on_ui_tabs(on_ui_tabs) 