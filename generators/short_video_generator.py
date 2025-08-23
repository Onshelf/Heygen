# generators/short_video_generator.py
import openai
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH

def generate_short_video_content(first_name, text, base_dir):
    """
    Generate short video content based on PDF text with separate files
    """
    short_video_dir = base_dir / "short video"
    short_video_dir.mkdir(parents=True, exist_ok=True)
    
    prompt = f"""
    Based EXCLUSIVELY on the following information about {first_name}:
    
    {text[:MAX_TEXT_LENGTH]}
    
    Create a short YouTube video package with the following components:
    
    1. SCRIPT: 200-word script starting with a HOOK and ending with a QUESTION asking viewers to comment
    2. DESCRIPTION: Professional video description with relevant hashtags and emojis
    3. IMAGE_PROMPTS: 2 detailed AI image generation prompts for visuals (specify which word they appear with)
    4. VIDEO_PROMPT: 1 detailed AI video generation prompt for a 5-second clip (specify which word it appears with)
    
    Format your response EXACTLY like this:

    [SCRIPT]
    Your script content here...

    [DESCRIPTION]
    Your description content here...

    [IMAGE_PROMPT_1]
    Your first image prompt here...
    [APPEARS_AT: specific word or phrase]

    [IMAGE_PROMPT_2]
    Your second image prompt here...
    [APPEARS_AT: specific word or phrase]

    [VIDEO_PROMPT]
    Your video prompt here...
    [APPEARS_AT: specific word or phrase]
    """

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional video content creator specializing in short-form content."},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Save complete response for reference
        with open(short_video_dir / "complete_response.txt", "w", encoding="utf-8") as f:
            f.write(f"Complete AI Response for {first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(content)
        
        # Parse and save individual components
        components = parse_video_components(content, first_name, short_video_dir)
        
        print(f"✅ Short video content generated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating short video content: {e}")
        return False

def parse_video_components(content, first_name, short_video_dir):
    """Parse and save individual video components to separate files"""
    try:
        # Save script
        if "[SCRIPT]" in content and "[DESCRIPTION]" in content:
            script = content.split("[SCRIPT]")[1].split("[DESCRIPTION]")[0].strip()
            with open(short_video_dir / "script.txt", "w", encoding="utf-8") as f:
                f.write(f"📝 Script for {first_name}\n")
                f.write("="*50 + "\n\n")
                f.write(script)
        
        # Save description
        if "[DESCRIPTION]" in content and "[IMAGE_PROMPT_1]" in content:
            description = content.split("[DESCRIPTION]")[1].split("[IMAGE_PROMPT_1]")[0].strip()
            with open(short_video_dir / "description.txt", "w", encoding="utf-8") as f:
                f.write(f"🏷️ Description for {first_name}\n")
                f.write("="*50 + "\n\n")
                f.write(description)
        
        # Save image prompts
        image_prompts = []
        for i in range(1, 3):
            start_tag = f"[IMAGE_PROMPT_{i}]"
            end_tag = f"[IMAGE_PROMPT_{i+1}]" if i < 2 else "[VIDEO_PROMPT]"
            
            if start_tag in content and end_tag in content:
                prompt_content = content.split(start_tag)[1].split(end_tag)[0].strip()
                image_prompts.append(prompt_content)
                
                with open(short_video_dir / f"image_prompt_{i}.txt", "w", encoding="utf-8") as f:
                    f.write(f"🎨 Image Prompt {i} for {first_name}\n")
                    f.write("="*50 + "\n\n")
                    f.write(prompt_content)
        
        # Save video prompt
        if "[VIDEO_PROMPT]" in content:
            video_prompt = content.split("[VIDEO_PROMPT]")[1].strip()
            with open(short_video_dir / "video_prompt.txt", "w", encoding="utf-8") as f:
                f.write(f"🎥 Video Prompt for {first_name}\n")
                f.write("="*50 + "\n\n")
                f.write(video_prompt)
                
    except Exception as e:
        print(f"⚠️ Error parsing video components: {e}")
