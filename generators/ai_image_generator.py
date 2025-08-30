# generators/ai_image_generator.py
import os
import requests
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Import from your existing API config
from utils.api_config import setup_wavespeed_api

def generate_ai_image(ai_prompt, output_path, width=1024, height=1024, image_name="generated_image.jpg"):
    """
    Generate AI image using the provided prompt and WaveSpeedAI API
    
    Args:
        ai_prompt (str or Path): AI image prompt text or path to prompt file
        output_path (Path): Directory or full path to save the generated image
        width (int): Image width in pixels (default: 1024)
        height (int): Image height in pixels (default: 1024)
        image_name (str): Name for the generated image file
    
    Returns:
        tuple: (success: bool, image_path: Path or None, error_message: str or None)
    """
    # Read prompt from file if a Path is provided
    if isinstance(ai_prompt, Path):
        try:
            with open(ai_prompt, 'r', encoding='utf-8') as f:
                prompt_text = f.read().strip()
        except FileNotFoundError:
            error_msg = f"AI image prompt file not found: {ai_prompt}"
            print(f"❌ {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Error reading AI image prompt: {e}"
            print(f"❌ {error_msg}")
            return False, None, error_msg
    else:
        prompt_text = str(ai_prompt).strip()
    
    if not prompt_text:
        error_msg = "AI image prompt is empty"
        print(f"❌ {error_msg}")
        return False, None, error_msg
    
    print(f"🎨 Using AI image prompt: {prompt_text[:100]}...")
    print(f"📐 Image size: {width}x{height}")
    
    # Get and validate API key using your existing config system
    API_KEY = setup_wavespeed_api()
    if not API_KEY:
        error_msg = "WaveSpeedAI API key is not configured or invalid"
        print(f"❌ {error_msg}")
        return False, None, error_msg
    
    # Configure API request
    url = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v3"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    
    # Set the specified image size
    image_size = f"{width}*{height}"
    
    payload = {
        "enable_base64_output": False,
        "enable_sync_mode": False,
        "guidance_scale": 2.5,
        "prompt": prompt_text,
        "seed": -1,
        "size": image_size
    }
    
    # Determine output directory and file path
    if output_path.is_dir():
        output_dir = output_path
        image_path = output_dir / image_name
    else:
        output_dir = output_path.parent
        image_path = output_path
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate image
    try:
        begin = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()["data"]
            request_id = result["id"]
            print(f"✅ Task submitted successfully. Request ID: {request_id}")
        else:
            error_msg = f"Error submitting task: {response.status_code}, {response.text}"
            print(f"❌ {error_msg}")
            return False, None, error_msg
        
        # Poll for results
        result_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
        
        max_attempts = 100  # 10 seconds maximum wait (100 attempts * 0.1s)
        attempts = 0
        
        while attempts < max_attempts:
            response = requests.get(result_url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()["data"]
                status = result["status"]
                
                if status == "completed":
                    end = time.time()
                    image_url = result["outputs"][0]
                    print(f"✅ Task completed in {end - begin:.2f} seconds.")
                    
                    # Download the image
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        # Save the image
                        with open(image_path, 'wb') as f:
                            f.write(image_response.content)
                        
                        print(f"✅ Image saved: {image_path}")
                        
                        # Also save the image URL for reference
                        url_path = output_dir / "image_url.txt"
                        with open(url_path, 'w', encoding='utf-8') as f:
                            f.write(image_url)
                        
                        return True, image_path, None
                    else:
                        error_msg = f"Error downloading image: {image_response.status_code}"
                        print(f"❌ {error_msg}")
                        return False, None, error_msg
                    
                elif status == "failed":
                    error_msg = f"Task failed: {result.get('error', 'Unknown error')}"
                    print(f"❌ {error_msg}")
                    return False, None, error_msg
                else:
                    # Still processing
                    attempts += 1
                    if attempts % 10 == 0:  # Print status every 10 attempts
                        print(f"⏳ Task still processing. Status: {status}")
                    time.sleep(0.1)
            else:
                error_msg = f"Error checking task status: {response.status_code}, {response.text}"
                print(f"❌ {error_msg}")
                return False, None, error_msg
        
        error_msg = "Task timed out - taking too long to process"
        print(f"❌ {error_msg}")
        return False, None, error_msg
        
    except Exception as e:
        error_msg = f"Error generating image: {e}"
        print(f"❌ {error_msg}")
        return False, None, error_msg


# Helper function for common use cases
def generate_image_from_prompt_file(prompt_file_path, output_dir, width=1024, height=1024, image_name="generated_image.jpg"):
    """
    Helper function to generate image from a prompt file
    
    Args:
        prompt_file_path (Path): Path to the AI image prompt file
        output_dir (Path): Directory to save the generated image
        width (int): Image width in pixels
        height (int): Image height in pixels
        image_name (str): Name for the generated image file
    
    Returns:
        tuple: (success: bool, image_path: Path or None, error_message: str or None)
    """
    return generate_ai_image(prompt_file_path, output_dir, width, height, image_name)


# Helper function for direct prompt text
def generate_image_from_prompt_text(prompt_text, output_path, width=1024, height=1024, image_name="generated_image.jpg"):
    """
    Helper function to generate image from prompt text
    
    Args:
        prompt_text (str): AI image prompt text
        output_path (Path): Directory or full path to save the generated image
        width (int): Image width in pixels
        height (int): Image height in pixels
        image_name (str): Name for the generated image file
    
    Returns:
        tuple: (success: bool, image_path: Path or None, error_message: str or None)
    """
    return generate_ai_image(prompt_text, output_path, width, height, image_name)
