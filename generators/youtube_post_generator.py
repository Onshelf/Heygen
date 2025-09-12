# generators/youtube_post_generator.py
import openai
import re
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH
from generators.ai_image_generator import generate_image_from_prompt_file  # Updated import

def generate_youtube_post(first_name, text, base_dir):
    """
    Generate YouTube post content based on PDF text
    """
    post_dir = base_dir / "post"
    post_dir.mkdir(parents=True, exist_ok=True)
    
    # Prompt for YouTube caption
    caption_prompt = f"""
    Based EXCLUSIVELY on the following information about {first_name}:
    
    {text[:MAX_TEXT_LENGTH]}
    
    Create an engaging YouTube caption (200-300 words) that includes:
    - Key highlights and interesting facts
    - Relevant emojis throughout the text
    - Hashtags related to the content
    - A call to action for viewers
    - Engaging and social media friendly tone
    
    Use ONLY the information provided above.
    """
    
    # Prompt for AI image generation
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

    try:
        # Generate YouTube caption
        caption_response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a skilled YouTube content writer and social media strategist. Create engaging, professional posts that capture attention, connect with the audience, and drive interaction. Use emojis thoughtfully to enhance readability and convey emotion, without overwhelming the message."},
                {"role": "user", "content": caption_prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=800
        )
        
        youtube_caption = caption_response.choices[0].message.content.strip()
        
        # Generate AI image prompt
        image_response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert in crafting detailed AI image generation prompts. Create precise and vivid prompts that fully capture the intended subject, mood, and style. Avoid including specific years, dates, or exact time periods, focusing instead on general eras, centuries, or timeless settings. Ensure clarity, creativity, and professional quality suitable for cinematic or illustrative outputs."},
                {"role": "user", "content": image_prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=500
        )
        
        ai_image_prompt = image_response.choices[0].message.content.strip()
        
        # Clean the AI image prompt - remove unwanted text and year references
        cleaned_image_prompt = clean_ai_prompt(ai_image_prompt, first_name)
        
        # Save YouTube caption to file
        with open(post_dir / "youtube_caption.txt", "w", encoding="utf-8") as f:
            f.write(youtube_caption)
        
        # Save cleaned AI image prompt to separate file
        with open(post_dir / "ai_image_prompt.txt", "w", encoding="utf-8") as f:
            f.write(cleaned_image_prompt)
        
        print(f"✅ YouTube post generated successfully!")
        print(f"📝 Caption saved: {post_dir}/youtube_caption.txt")
        print(f"🎨 Image prompt saved: {post_dir}/ai_image_prompt.txt")
        
        # Generate AI image using the prompt with YouTube thumbnail size
        print("🖼️ Generating AI image from prompt...")
        ai_prompt_file = post_dir / "ai_image_prompt.txt"
        success, image_path, error = generate_image_from_prompt_file(
            ai_prompt_file, 
            post_dir, 
            width=1024, 
            height=1024, 
            image_name="youtube_thumbnail.jpg"
        )
        
        if success:
            print("✅ AI image generated successfully!")
            return True
        else:
            print(f"❌ AI image generation failed: {error}")
            return False
        
    except Exception as e:
        print(f"❌ Error generating YouTube post: {e}")
        return False

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
