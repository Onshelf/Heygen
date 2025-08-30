# utils/api_config.py
import openai
import os
import requests
from dotenv import load_dotenv

def setup_openai_api():
    """
    Set up OpenAI API configuration
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "API":
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Please add OPENAI_API_KEY=your_key_here to your .env file")
        return False
    
    openai.api_key = api_key
    print("✅ OpenAI API configured successfully")
    return True

def setup_wavespeed_api():
    """
    Set up and validate WaveSpeedAI API configuration
    Returns: API key if valid, None otherwise
    """
    load_dotenv()
    api_key = os.getenv("WAVESPEED_API_KEY")
    
    if not api_key:
        print("❌ WAVESPEED_API_KEY not found in environment variables")
        print("💡 Please add WAVESPEED_API_KEY=your_key_here to your .env file")
        return None
    
    # Test if the API key is valid by making a simple request
    try:
        url = "https://api.wavespeed.ai/api/v3/predictions"
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ WaveSpeedAI API configured successfully")
            return api_key
        elif response.status_code == 401:
            print("❌ Invalid WaveSpeedAI API key: Unauthorized")
            return None
        else:
            print(f"⚠️ WaveSpeedAI API key test returned status: {response.status_code}")
            # Still return the key as it might work for image generation
            return api_key
            
    except Exception as e:
        print(f"⚠️ Could not validate WaveSpeedAI API key (may still work): {e}")
        return api_key
