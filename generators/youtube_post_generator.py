# generators/youtube_post_generator.py
import openai
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH

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
    - Technical details (4K, ultra detailed, professional photography)
    - Camera angle and composition
    
    Make it comprehensive and suitable for AI image models like DALL-E, Midjourney, or Stable Diffusion.
    """

    try:
        # Generate YouTube caption
        caption_response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a creative social media content creator who uses emojis effectively."},
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
                {"role": "system", "content": "You are an expert at creating detailed AI image generation prompts."},
                {"role": "user", "content": image_prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=500
        )
        
        ai_image_prompt = image_response.choices[0].message.content.strip()
        
        # Save YouTube caption to file
        with open(post_dir / "youtube_caption.txt", "w", encoding="utf-8") as f:
            f.write(f"🎬 YouTube Caption for {first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(youtube_caption)
        
        # Save AI image prompt to separate file
        with open(post_dir / "ai_image_prompt.txt", "w", encoding="utf-8") as f:
            f.write(f"🎨 AI Image Prompt for {first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(ai_image_prompt)
        
        print(f"✅ YouTube post generated successfully!")
        print(f"📝 Caption saved: {post_dir}/youtube_caption.txt")
        print(f"🎨 Image prompt saved: {post_dir}/ai_image_prompt.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error generating YouTube post: {e}")
        return False
