# generators/long_video_generator.py
import openai
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH

def generate_long_video_content(first_name, text, base_dir):
    """
    Generate professional long video content based on PDF text with separate files
    """
    long_video_dir = base_dir / "long video"
    long_video_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 10 image prompts using the same format as YouTube generator
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
- Technical details (4K, ultra detailed, professional photography)
- Camera angle and composition

Make it comprehensive and suitable for AI image models like DALL-E, Midjourney, or Stable Diffusion.

IMPORTANT: DO NOT create prompts showing historical figures as children with their parents.
"""

        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at creating detailed AI image generation prompts. Focus on professional visual descriptions and avoid childhood family scenes."},
                    {"role": "user", "content": image_prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=500
            )
            
            prompt_content = response.choices[0].message.content.strip()
            image_prompts.append(prompt_content)
            
            # Save each image prompt to separate file
            with open(long_video_dir / f"image_prompt_{i}.txt", "w", encoding="utf-8") as f:
                f.write(f"🎨 Image Prompt {i} for {first_name}\n")
                f.write("="*50 + "\n\n")
                f.write(prompt_content)
                
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
- Technical specifications for video quality
- Composition and framing

Make it suitable for AI video models and avoid any childhood family scenes.
"""

        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at creating detailed AI video generation prompts. Focus on cinematic quality and avoid prohibited content."},
                    {"role": "user", "content": video_prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=400
            )
            
            prompt_content = response.choices[0].message.content.strip()
            video_prompts.append(prompt_content)
            
            # Save each video prompt to separate file
            with open(long_video_dir / f"video_prompt_{i}.txt", "w", encoding="utf-8") as f:
                f.write(f"🎥 Video Prompt {i} for {first_name}\n")
                f.write("="*50 + "\n\n")
                f.write(prompt_content)
                
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
            f.write(f"🎬 Documentary Script: {first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(script_content)
        
        print(f"✅ Long video content generated successfully!")
        print(f"📝 Script and {len(image_prompts)} image prompts, {len(video_prompts)} video prompts saved")
        return True
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        return False
