# generators/long_video_generator.py
import openai
import re
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH
from generators.ai_image_generator import generate_image_from_prompt_file  # Import the AI image generator
from generators.ai_video_generator import generate_ai_video, VideoGenerationError  # Import the AI video generator

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
        
        # Generate thumbnail prompt for the long video
        thumbnail_prompt = generate_thumbnail_prompt(first_name, text)
        if thumbnail_prompt:
            with open(long_video_dir / "thumbnail_prompt.txt", "w", encoding="utf-8") as f:
                f.write(thumbnail_prompt)
        
        # Generate AI images from the prompts (all in 1280x720 format)
        image_success = generate_ai_images_from_prompts(long_video_dir)
        
        # Generate AI videos from the video prompts (5 seconds, 16:9 aspect ratio)
        video_success = generate_ai_videos_from_prompts(long_video_dir)
        
        print(f"✅ Long video content generated successfully!")
        print(f"📝 Script and {len(image_prompts)} image prompts, {len(video_prompts)} video prompts saved")
        return True and image_success and video_success
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        return False

def generate_ai_videos_from_prompts(long_video_dir):
    """
    Generate AI videos from the video prompt files in the long video directory
    Uses 5-second duration and 16:9 aspect ratio for documentary-style content
    """
    try:
        video_success = True
        
        # Generate videos for each video prompt (up to 4 prompts)
        for i in range(1, 5):
            video_prompt_file = long_video_dir / f"video_prompt_{i}.txt"
            
            if video_prompt_file.exists():
                print(f"🎬 Generating AI video {i} from prompt...")
                
                # Read the video prompt
                with open(video_prompt_file, "r", encoding="utf-8") as f:
                    video_prompt = f.read().strip()
                
                if not video_prompt:
                    print(f"❌ Video prompt {i} is empty")
                    video_success = False
                    continue
                
                # Generate video with fixed 5-second duration and 16:9 aspect ratio
                try:
                    video_url = generate_ai_video(
                        prompt=video_prompt,
                        duration=5,           # Fixed 5-second duration
                        aspect_ratio="16:9",  # Fixed documentary aspect ratio
                        timeout=600           # 10 minute timeout for video generation
                    )
                    
                    # Save the video URL
                    with open(long_video_dir / f"video_url_{i}.txt", "w", encoding="utf-8") as f:
                        f.write(video_url)
                    
                    print(f"✅ AI video {i} generated successfully!")
                    
                except VideoGenerationError as e:
                    print(f"❌ AI video {i} generation failed: {e}")
                    video_success = False
                except Exception as e:
                    print(f"❌ Unexpected error generating AI video {i}: {e}")
                    video_success = False
            else:
                print(f"❌ Video prompt file {i} not found")
                video_success = False
        
        return video_success
        
    except Exception as e:
        print(f"❌ Error generating AI videos: {e}")
        return False

def generate_thumbnail_prompt(first_name, text):
    """
    Generate a professional thumbnail prompt for the long video
    """
    thumbnail_prompt = f"""
Based EXCLUSIVELY on the following information about {first_name}:

{text[:MAX_TEXT_LENGTH]}

Create a detailed professional AI image generation prompt specifically for a YouTube thumbnail that:
- Features {first_name} in a powerful, authoritative pose
- Uses cinematic, dramatic lighting with high contrast
- Includes a compelling focal point that draws attention
- Has a professional, polished appearance suitable for documentary content
- Uses a color palette that conveys importance and gravitas
- Includes negative space for title text overlay
- Looks like a professional documentary film poster

IMPORTANT: 
- DO NOT include specific years, dates, or time periods in the prompt.
- Focus on adult professional appearance, not childhood.
- Make it visually striking and click-worthy.
"""

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert at creating compelling YouTube thumbnail prompts. Create professional, cinematic prompts that would drive high click-through rates for documentary content."},
                {"role": "user", "content": thumbnail_prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=400
        )
        
        prompt_content = response.choices[0].message.content.strip()
        return clean_ai_prompt(prompt_content, first_name)
        
    except Exception as e:
        print(f"❌ Error generating thumbnail prompt: {e}")
        return None

def generate_ai_images_from_prompts(long_video_dir):
    """
    Generate AI images from the prompt files in the long video directory
    ALL images use 1280x720 format for documentary-style content
    """
    try:
        image_success = True
        
        # Generate images for each image prompt (up to 10 prompts)
        for i in range(1, 11):
            prompt_file = long_video_dir / f"image_prompt_{i}.txt"
            
            if prompt_file.exists():
                print(f"🖼️ Generating AI image {i} from prompt...")
                
                # Use documentary format (1280x720) for long video content
                success, image_path, error = generate_image_from_prompt_file(
                    prompt_file, 
                    long_video_dir, 
                    width=1280, 
                    height=720, 
                    image_name=f"long_video_image_{i}.jpg"
                )
                
                if success:
                    print(f"✅ AI image {i} generated successfully!")
                else:
                    print(f"❌ AI image {i} generation failed: {error}")
                    image_success = False
        
        # Generate thumbnail image (also in 1280x720 format)
        thumbnail_prompt_file = long_video_dir / "thumbnail_prompt.txt"
        if thumbnail_prompt_file.exists():
            print("🖼️ Generating thumbnail image from prompt...")
            
            # Use documentary format (1280x720) for thumbnail
            success, image_path, error = generate_image_from_prompt_file(
                thumbnail_prompt_file, 
                long_video_dir, 
                width=1280, 
                height=720, 
                image_name="long_video_thumbnail.jpg"
            )
            
            if success:
                print("✅ Thumbnail image generated successfully!")
            else:
                print(f"❌ Thumbnail image generation failed: {error}")
                image_success = False
        
        return image_success
        
    except Exception as e:
        print(f"❌ Error generating AI images: {e}")
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
