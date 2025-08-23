# generators/long_video_generator.py
import openai
import re
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH

def generate_long_video_content(first_name, text, base_dir):
    """
    Generate professional long video content based on PDF text with separate files
    """
    long_video_dir = base_dir / "long video"
    long_video_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 10 image prompts using the consistent format
    image_prompts = []
    for i in range(1, 11):
        image_prompt = f"""
Based EXCLUSIVELY on the following information about {first_name}:

{text[:MAX_TEXT_LENGTH]}

Create a detailed professional AI image generation prompt that includes:
- Visual description of the main subject
- Setting and background context
- Style and artistic direction (photorealistic, cinematic, illustration, etc.)
- Lighting and mood specifications
- Camera angle and composition

Make it comprehensive and suitable for AI image models like DALL-E, Midjourney, or Stable Diffusion.

IMPORTANT: 
- DO NOT include specific years, dates, or time periods in the prompt.
- DO NOT create prompts showing historical figures as children with their parents.
"""

        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at creating detailed AI image generation prompts. Avoid including specific years or time periods and focus on professional visual descriptions."},
                    {"role": "user", "content": image_prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=500
            )
            
            prompt_content = response.choices[0].message.content.strip()
            cleaned_prompt = clean_ai_prompt(prompt_content, first_name)
            image_prompts.append(cleaned_prompt)
            
            # Save each cleaned image prompt to separate file
            with open(long_video_dir / f"image_prompt_{i}.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_prompt)
                
        except Exception as e:
            print(f"❌ Error generating image prompt {i}: {e}")
            image_prompts.append("")
    
    # Generate 4 video prompts
    video_prompts = []
    for i in range(1, 5):
        video_prompt = f"""
Based EXCLUSIVELY on the following information about {first_name}:

{text[:MAX_TEXT_LENGTH]}

Create a detailed professional AI video generation prompt for a 5-second cinematic clip that includes:
- Visual description of the scene and subjects
- Camera movement and angles
- Lighting and atmosphere
- Style and mood (cinematic, documentary, dramatic, etc.)
- Composition and framing

Make it suitable for AI video models and avoid any childhood family scenes.

IMPORTANT: DO NOT include specific years, dates, or time periods in the prompt.
"""

        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at creating detailed AI video generation prompts. Avoid including specific years or time periods and focus on cinematic quality."},
                    {"role": "user", "content": video_prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=400
            )
            
            prompt_content = response.choices[0].message.content.strip()
            cleaned_prompt = clean_ai_prompt(prompt_content, first_name)
            video_prompts.append(cleaned_prompt)
            
            # Save each cleaned video prompt to separate file
            with open(long_video_dir / f"video_prompt_{i}.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_prompt)
                
        except Exception as e:
            print(f"❌ Error generating video prompt {i}: {e}")
            video_prompts.append("")
    
    # Generate the main script
    script_prompt = f"""
Based EXCLUSIVELY on the following information about {first_name}:

{text[:MAX_TEXT_LENGTH]}

Create a 3000-word professional documentary script that includes:
- Engaging introduction that starts immediately with content
- Comprehensive coverage of the subject's life and achievements
- Natural transitions between topics
- Professional narration style
- Strong conclusion with call to action

Focus on the subject's adult life and professional achievements.
Avoid detailing childhood family scenes.
"""

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an award-winning documentary filmmaker. Create professional, engaging scripts that focus on adult achievements."},
                {"role": "user", "content": script_prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=3500
        )
        
        script_content = response.choices[0].message.content.strip()
        
        # Save the script
        with open(long_video_dir / "script.txt", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print(f"✅ Long video content generated successfully!")
        print(f"📝 Script and {len(image_prompts)} image prompts, {len(video_prompts)} video prompts saved")
        return True
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        return False

def clean_ai_prompt(prompt_text, first_name):
    """
    Clean the AI image prompt by removing unwanted introductory text and year references
    while preserving the name and descriptive content
    """
    # Remove common introductory patterns but keep the name in the content
    patterns_to_remove = [
        "**AI Image Generation Prompt:**",
        "**AI Video Generation Prompt:**",
        "This prompt is designed to create",
        "capturing not just his physical likeness",
        "the essence of his legacy",
        "one of the greatest minds in history",
        "==================================================",
        "**Prompt:**",
        "Here is a detailed AI image generation prompt:",
        "Here is a detailed AI video generation prompt:",
    ]
    
    cleaned_prompt = prompt_text
    for pattern in patterns_to_remove:
        cleaned_prompt = cleaned_prompt.replace(pattern, "")
    
    # Remove specific year references (e.g., "in 1947", "from 1920", "during the 1950s")
    cleaned_prompt = re.sub(r'\b(in|from|during|of|circa)\s+\d{4}s?\b', '', cleaned_prompt, flags=re.IGNORECASE)
    cleaned_prompt = re.sub(r'\b\d{4}s?\b', '', cleaned_prompt)
    
    # Remove any phrases that start with creation verbs but preserve the name
    # Only remove if they're at the very beginning
    if re.match(r'^(Create|Generate|Make|Design|Produce)\s+(a|an|the)?\s+', cleaned_prompt, re.IGNORECASE):
        # Replace the command but keep the rest including the name
        cleaned_prompt = re.sub(r'^(Create|Generate|Make|Design|Produce)\s+(a|an|the)?\s*', '', cleaned_prompt, flags=re.IGNORECASE)
    
    # Remove any double newlines and clean up whitespace
    cleaned_prompt = "\n".join([line.strip() for line in cleaned_prompt.split("\n") if line.strip()])
    cleaned_prompt = cleaned_prompt.strip()
    
    # Ensure the prompt starts with descriptive content, not creation commands
    if cleaned_prompt.startswith(('a ', 'an ', 'the ')):
        cleaned_prompt = cleaned_prompt[0].upper() + cleaned_prompt[1:]
    
    return cleaned_prompt
