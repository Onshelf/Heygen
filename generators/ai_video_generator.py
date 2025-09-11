# generators/ai_video_generator.py
import os
import requests
import json
import time
import re
from typing import Optional, Tuple
from pathlib import Path

# Import from your existing API config
from utils.api_config import setup_wavespeed_api

class VideoGenerationError(Exception):
    """Custom exception for video generation errors"""
    pass

def parse_video_size_from_prompt(prompt: str) -> Tuple[int, str, str]:
    """
    Parse video duration and aspect ratio from prompt metadata
    
    Args:
        prompt (str): The prompt string that may contain metadata
    
    Returns:
        Tuple[int, str, str]: (duration, aspect_ratio, clean_prompt)
    """
    # Default values
    duration = 5  # seconds
    aspect_ratio = "16:9"
    
    # Look for metadata patterns in the prompt
    patterns = [
        r"\[duration:(\d+)\]",  # [duration:10]
        r"\[length:(\d+)\]",    # [length:8]
        r"\[time:(\d+)\]",      # [time:15]
        r"\[aspect:([\d]+:[\d]+)\]",  # [aspect:9:16]
        r"\[ratio:([\d]+:[\d]+)\]",   # [ratio:1:1]
        r"\[size:([\d]+:[\d]+)\]",    # [size:16:9]
    ]
    
    clean_prompt = prompt
    
    # Extract duration
    for pattern in patterns[:3]:
        match = re.search(pattern, clean_prompt, re.IGNORECASE)
        if match:
            duration = int(match.group(1))
            # Remove the metadata from the prompt
            clean_prompt = clean_prompt.replace(match.group(0), "").strip()
            break
    
    # Extract aspect ratio
    for pattern in patterns[3:]:
        match = re.search(pattern, clean_prompt, re.IGNORECASE)
        if match:
            aspect_ratio = match.group(1)
            # Remove the metadata from the prompt
            clean_prompt = clean_prompt.replace(match.group(0), "").strip()
            break
    
    return duration, aspect_ratio, clean_prompt

def generate_ai_video(
    prompt: str,
    duration: Optional[int] = None,
    aspect_ratio: Optional[str] = None,
    camera_fixed: bool = False,
    seed: int = -1,
    poll_interval: float = 2.0,
    timeout: int = 600
) -> str:
    """
    Generate a video using WaveSpeed AI API with automatic size detection from prompt
    
    Args:
        prompt (str): The text prompt for video generation (may contain metadata)
        duration (int, optional): Video length in seconds. If None, extracted from prompt
        aspect_ratio (str, optional): Video aspect ratio. If None, extracted from prompt
        camera_fixed (bool): Whether to use fixed camera (default: False)
        seed (int): Random seed for reproducibility (default: -1 for random)
        poll_interval (float): Interval between polling requests in seconds
        timeout (int): Maximum time to wait for completion in seconds
    
    Returns:
        str: URL of the generated video
    
    Raises:
        VideoGenerationError: If video generation fails
    """
    # Parse metadata from prompt if not explicitly provided
    parsed_duration, parsed_aspect, clean_prompt = parse_video_size_from_prompt(prompt)
    
    # Use provided values or fall back to parsed values
    final_duration = duration if duration is not None else parsed_duration
    final_aspect = aspect_ratio if aspect_ratio is not None else parsed_aspect
    
    # Get API key using your existing config system
    api_key = setup_wavespeed_api()
    if not api_key:
        raise VideoGenerationError("WaveSpeedAI API key is not configured or invalid")
    
    # Validate inputs
    if not clean_prompt or not clean_prompt.strip():
        raise VideoGenerationError("Prompt cannot be empty")
    
    if final_duration <= 0:
        raise VideoGenerationError("Duration must be positive")
    
    if not final_aspect or ":" not in final_aspect:
        raise VideoGenerationError("Invalid aspect ratio format. Use 'width:height'")
    
    # Updated API configuration with new endpoint
    url = "https://api.wavespeed.ai/api/v3/wavespeed-ai/wan-2.2/t2v-480p-ultra-fast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    payload = {
        "aspect_ratio": final_aspect,
        "camera_fixed": camera_fixed,
        "duration": final_duration,
        "prompt": clean_prompt,
        "seed": seed
    }
    
    print(f"🎬 Generating video:")
    print(f"   Prompt: {clean_prompt}")
    print(f"   Duration: {final_duration}s")
    print(f"   Aspect Ratio: {final_aspect}")
    
    # Submit generation request
    begin = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.exceptions.Timeout:
        raise VideoGenerationError("API request timeout")
    except requests.exceptions.RequestException as e:
        raise VideoGenerationError(f"API request failed: {e}")
    
    if response.status_code != 200:
        raise VideoGenerationError(
            f"API request failed: {response.status_code}, {response.text}"
        )
    
    try:
        result = response.json()["data"]
        request_id = result["id"]
        print(f"✅ Task submitted. Request ID: {request_id}")
    except (KeyError, ValueError) as e:
        raise VideoGenerationError(f"Invalid API response format: {e}")
    
    # Poll for results
    result_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    result_headers = {"Authorization": f"Bearer {api_key}"}
    
    poll_start = time.time()
    poll_count = 0
    
    while True:
        poll_count += 1
        
        # Check timeout
        if time.time() - poll_start > timeout:
            raise VideoGenerationError(f"Generation timeout after {timeout} seconds")
        
        # Wait before polling (longer wait after first few polls)
        if poll_count > 5:
            time.sleep(poll_interval * 2)  # Longer wait after initial polls
        else:
            time.sleep(poll_interval)
        
        try:
            response = requests.get(result_url, headers=result_headers, timeout=30)
        except requests.exceptions.Timeout:
            print("⏳ Polling timeout, retrying...")
            continue
        except requests.exceptions.RequestException as e:
            print(f"⏳ Polling error: {e}, retrying...")
            continue
        
        if response.status_code != 200:
            print(f"⏳ Polling failed: {response.status_code}, retrying...")
            continue
        
        try:
            result = response.json()["data"]
            status = result["status"]
            
            if status == "completed":
                end_time = time.time()
                total_time = end_time - begin
                video_url = result["outputs"][0]
                print(f"✅ Video generated in {total_time:.2f} seconds")
                print(f"📹 Video URL: {video_url}")
                return video_url
            
            elif status == "failed":
                error_msg = result.get('error', 'Unknown error')
                raise VideoGenerationError(f"Task failed: {error_msg}")
            
            else:
                print(f"⏳ Processing... Status: {status}")
                
        except (KeyError, ValueError) as e:
            print(f"⏳ Invalid polling response: {e}, retrying...")
            continue

# Convenience function for short videos
def generate_short_video(prompt: str, **kwargs) -> str:
    """
    Generate a short video (default 5-15 seconds)
    
    Args:
        prompt (str): The text prompt for video generation
        **kwargs: Additional arguments passed to generate_ai_video
    
    Returns:
        str: URL of the generated video
    """
    return generate_ai_video(prompt, **kwargs)

# Convenience function for long videos
def generate_long_video(prompt: str, **kwargs) -> str:
    """
    Generate a long video (default 30-60 seconds)
    
    Args:
        prompt (str): The text prompt for video generation
        **kwargs: Additional arguments passed to generate_ai_video
    
    Returns:
        str: URL of the generated video
    """
    # Force longer duration unless explicitly overridden
    if 'duration' not in kwargs:
        kwargs['duration'] = 30
    
    return generate_ai_video(prompt, **kwargs)

# Main function for standalone testing
def main():
    """Test function for standalone execution"""
    try:
        # Example with metadata in prompt
        test_prompt = "A beautiful sunset over mountains [duration:8] [aspect:9:16] with vibrant colors"
        
        video_url = generate_ai_video(test_prompt)
        print(f"Test successful! Video URL: {video_url}")
        
    except VideoGenerationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
