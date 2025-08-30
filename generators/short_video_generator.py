# generators/short_video_generator.py
import openai
import re
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH
from generators.ai_image_generator import generate_image_from_prompt_file  # Import the AI image generator
from generators.ai_video_generator import generate_ai_video, VideoGenerationError  # Import the AI video generator

def generate_short_video_content(first_name, text, base_dir):
    """
    Generate short video content based on PDF text with separate files
    """
    short_video_dir = base_dir / "short video"
    short_video_dir.mkdir(parents=True, exist_ok=True)
    
    # Prompt for AI image generation (consistent with youtube_post_generator)
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
    
    IMPORTANT: DO NOT include specific years, dates, or time periods in the prompt.
    """
    
    prompt = f"""
    Based EXCLUSIVELY on the following information about {first_name}:
    
    {text[:MAX_TEXT_LENGTH]}
    
    Create a short YouTube Shorts/TikTok/Instagram Reels video package with the following components:
    
    1. SCRIPT: 200-word script starting with a HOOK and ending with a QUESTION asking viewers to comment
    2. DESCRIPTION: Professional video description with relevant hashtags and emojis
    3. IMAGE_PROMPTS: 2 detailed AI image generation prompts for visuals (specify which word they appear with)
    4. VIDEO_PROMPT: 1 detailed AI video generation prompt for a 5-second clip (specify which word it appears with)
    5. THUMBNAIL_PROMPT: 1 detailed AI image generation prompt specifically for a vertical thumbnail (720x1280)
    
    For the image prompts, use this format and level of detail:
    {image_prompt}
    
    For the THUMBNAIL_PROMPT, create a compelling vertical thumbnail (720x1280) that:
    - Features a clear, high-contrast focal point in vertical composition
    - Uses bold, eye-catching colors optimized for mobile viewing
    - Includes expressive facial expression if appropriate
    - Has a mysterious or intriguing element to drive clicks
    - Uses professional photography style with dramatic lighting
    - Includes negative space at the top or bottom for potential text overlay
    - Optimized for vertical mobile viewing
    
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

    [THUMBNAIL_PROMPT]
    Your thumbnail prompt here...
    """

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional video content creator specializing in short-form vertical content. Avoid including specific years or time periods in visual prompts. Create compelling, click-worthy thumbnail prompts optimized for 720x1280 vertical format."},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=2800  # Increased tokens for additional thumbnail prompt
        )
        
        content = response.choices[0].message.content.strip()
        
        # Save complete response for reference
        with open(short_video_dir / "complete_response.txt", "w", encoding="utf-8") as f:
            f.write(f"Complete AI Response for {first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(content)
        
        # Parse and save individual components
        components = parse_video_components(content, first_name, short_video_dir)
        
        # Generate AI images from the prompts (all in 720x1280 format)
        image_success = generate_ai_images_from_prompts(short_video_dir)
        
        # Generate AI video from the video prompt (5 seconds, 9:16 aspect ratio)
        video_success = generate_ai_video_from_prompt(short_video_dir)
        
        print(f"✅ Short video content generated successfully!")
        return True and image_success and video_success  # Return True only if all generations succeeded
        
    except Exception as e:
        print(f"❌ Error generating short video content: {e}")
        return False

def generate_ai_video_from_prompt(short_video_dir):
    """
    Generate AI video from the video prompt file
    Uses 5-second duration and 9:16 aspect ratio
    """
    try:
        video_prompt_file = short_video_dir / "video_prompt.txt"
        
        if video_prompt_file.exists():
            print("🎬 Generating AI video from prompt...")
            
            # Read the video prompt
            with open(video_prompt_file, "r", encoding="utf-8") as f:
                video_prompt = f.read().strip()
            
            if not video_prompt:
                print("❌ Video prompt is empty")
                return False
            
            # Generate video with fixed 5-second duration and 9:16 aspect ratio
            video_url = generate_ai_video(
                prompt=video_prompt,
                duration=5,           # Fixed 5-second duration
                aspect_ratio="9:16",  # Fixed vertical aspect ratio
                timeout=600           # 10 minute timeout for video generation
            )
            
            # Save the video URL
            with open(short_video_dir / "video_url.txt", "w", encoding="utf-8") as f:
                f.write(video_url)
            
            print("✅ AI video generated successfully!")
            return True
        else:
            print("❌ Video prompt file not found")
            return False
            
    except VideoGenerationError as e:
        print(f"❌ AI video generation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error generating AI video: {e}")
        return False

def generate_ai_images_from_prompts(short_video_dir):
    """
    Generate AI images from the prompt files in the short video directory
    ALL images use 720x1280 vertical format
    """
    try:
        image_success = True
        
        # Generate images for each image prompt (up to 2 prompts)
        for i in range(1, 3):
            prompt_file = short_video_dir / f"image_prompt_{i}.txt"
            
            if prompt_file.exists():
                print(f"🖼️ Generating AI image {i} from prompt...")
                
                # Use vertical format (720x1280) for all short video content
                success, image_path, error = generate_image_from_prompt_file(
                    prompt_file, 
                    short_video_dir, 
                    width=720, 
                    height=1280, 
                    image_name=f"short_video_image_{i}.jpg"
                )
                
                if success:
                    print(f"✅ AI image {i} generated successfully!")
                else:
                    print(f"❌ AI image {i} generation failed: {error}")
                    image_success = False
        
        # Generate thumbnail image (also in 720x1280 vertical format)
        thumbnail_prompt_file = short_video_dir / "thumbnail_prompt.txt"
        if thumbnail_prompt_file.exists():
            print("🖼️ Generating thumbnail image from prompt...")
            
            # Use vertical format (720x1280) for thumbnail as well
            success, image_path, error = generate_image_from_prompt_file(
                thumbnail_prompt_file, 
                short_video_dir, 
                width=720, 
                height=1280, 
                image_name="short_video_thumbnail.jpg"
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

def parse_video_components(content, first_name, short_video_dir):
    """Parse and save individual video components to separate files"""
    try:
        # Save script
        if "[SCRIPT]" in content and "[DESCRIPTION]" in content:
            script = content.split("[SCRIPT]")[1].split("[DESCRIPTION]")[0].strip()
            with open(short_video_dir / "script.txt", "w", encoding="utf-8") as f:
                f.write(script)
        
        # Save description
        if "[DESCRIPTION]" in content and "[IMAGE_PROMPT_1]" in content:
            description = content.split("[DESCRIPTION]")[1].split("[IMAGE_PROMPT_1]")[0].strip()
            with open(short_video_dir / "description.txt", "w", encoding="utf-8") as f:
                f.write(description)
        
        # Save image prompts (cleaned)
        image_prompts = []
        for i in range(1, 3):
            start_tag = f"[IMAGE_PROMPT_{i}]"
            end_tag = f"[IMAGE_PROMPT_{i+1}]" if i < 2 else "[VIDEO_PROMPT]"
            
            if start_tag in content and end_tag in content:
                prompt_content = content.split(start_tag)[1].split(end_tag)[0].strip()
                # Remove the [APPEARS_AT] line if present
                if "[APPEARS_AT:" in prompt_content:
                    prompt_content = prompt_content.split("[APPEARS_AT:")[0].strip()
                cleaned_prompt = clean_ai_prompt(prompt_content, first_name)
                image_prompts.append(cleaned_prompt)
                
                with open(short_video_dir / f"image_prompt_{i}.txt", "w", encoding="utf-8") as f:
                    f.write(cleaned_prompt)
        
        # Save video prompt (cleaned)
        if "[VIDEO_PROMPT]" in content and "[THUMBNAIL_PROMPT]" in content:
            video_prompt = content.split("[VIDEO_PROMPT]")[1].split("[THUMBNAIL_PROMPT]")[0].strip()
            # Remove the [APPEARS_AT] line if present
            if "[APPEARS_AT:" in video_prompt:
                video_prompt = video_prompt.split("[APPEARS_AT:")[0].strip()
            cleaned_video_prompt = clean_ai_prompt(video_prompt, first_name)
            with open(short_video_dir / "video_prompt.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_video_prompt)
        
        # Save thumbnail prompt (cleaned)
        if "[THUMBNAIL_PROMPT]" in content:
            thumbnail_prompt = content.split("[THUMBNAIL_PROMPT]")[1].strip()
            cleaned_thumbnail_prompt = clean_ai_prompt(thumbnail_prompt, first_name)
            with open(short_video_dir / "thumbnail_prompt.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_thumbnail_prompt)
                
    except Exception as e:
        print(f"⚠️ Error parsing video components: {e}")

def clean_ai_prompt(prompt_text, first_name):
    """
    Clean the AI image prompt by removing unwanted introductory text and year references
    while preserving the name and descriptive content
    """
    # Remove common introductory patterns but keep the name in the content
    patterns_to_remove = [
        "**AI Image Generation Prompt:**",
        "This prompt is designed to create",
        "capturing not just his physical likeness",
        "the essence of his legacy",
        "one of the greatest minds in history",
        "==================================================",
        "**Prompt:**",
        "Here is a detailed AI image generation prompt:",
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
