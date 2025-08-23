# utils/api_config.py
import openai
import os

def setup_openai_api():
    """
    Set up OpenAI API configuration
    """
    openai.api_key = os.getenv("OPENAI_API_KEY", "API")
    print("✅ OpenAI API configured successfully")
    return True
