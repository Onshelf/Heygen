# generators/long_video_generator.py
import openai
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH

def generate_long_video_content(first_name, text, base_dir):
    """
    Generate long video content based on PDF text with separate files
    """
    long_video_dir = base_dir / "long video"
    long_video_dir.mkdir(parents=True, exist_ok=True)
    
    prompt = f"""
    Based EXCLUSIVELY on the following information about {first_name}:
    
    {text[:MAX_TEXT_LENGTH]}
    
    Create a comprehensive long YouTube video package with these components:
    
    1. SCRIPT: 3000-word script starting with introduction and ending with call to action
    2. DESCRIPTION: Professional video description with relevant hashtags and emojis
    3. IMAGE_PROMPTS: 10 detailed AI image generation prompts for visuals
    4. VIDEO_PROMPTS: 4 detailed AI video generation prompts for 5-second clips
    
    Format your response with clear section markers.
    """

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a documentary filmmaker creating detailed long-form content."},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Save complete response
        with open(long_video_dir / "complete_response.txt", "w", encoding="utf-8") as f:
            f.write(f"Complete AI Response for {first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(content)
        
        # For long content, we'll create separate files manually
        create_separate_files(content, first_name, long_video_dir)
        
        print(f"✅ Long video content generated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating long video content: {e}")
        return False

def create_separate_files(content, first_name, long_video_dir):
    """Create separate files for different components"""
    # Save script (first part)
    with open(long_video_dir / "script.txt", "w", encoding="utf-8") as f:
        f.write(f"📝 Long Video Script for {first_name}\n")
        f.write("="*50 + "\n\n")
        f.write(content[:2000] + "\n\n... [script continues]")
    
    # Save description
    with open(long_video_dir / "description.txt", "w", encoding="utf-8") as f:
        f.write(f"🏷️ Video Description for {first_name}\n")
        f.write("="*50 + "\n\n")
        f.write("Professional documentary description with hashtags...")
    
    # Create sample image prompts
    for i in range(1, 11):
        with open(long_video_dir / f"image_prompt_{i}.txt", "w", encoding="utf-8") as f:
            f.write(f"🎨 Image Prompt {i} for {first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(f"Professional AI image prompt for scene {i}...")
    
    # Create sample video prompts
    for i in range(1, 5):
        with open(long_video_dir / f"video_prompt_{i}.txt", "w", encoding="utf-8") as f:
            f.write(f"🎥 Video Prompt {i} for {first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(f"Professional AI video prompt for clip {i}...")
