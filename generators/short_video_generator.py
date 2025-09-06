# generators/short_video_generator.py
import openai
import re
from pathlib import Path
from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, MAX_TEXT_LENGTH
from generators.ai_image_generator import generate_image_from_prompt_file  # Import the AI image generator
from generators.ai_video_generator import generate_ai_video, VideoGenerationError  # Import the AI video generator

# List of restricted words that cannot be in the final prompts
RESTRICTED_WORDS = [
    "strike", "attack", "kill", "murder", "shoot", "shot", "stab", "blood", "gore", "bomb", 
    "gun", "rifle", "pistol", "knife", "sword", "chainsaw", "explosion", "massacre", "execution", 
    "decapitate", "torture", "mutilation", "behead", "slaughter", "corpse", "cadaver", "weapon", 
    "bullet", "grenade", "mine", "missile", "war", "combat", "battlefield", "militia", "insurgent", 
    "fighter", "assassination", "terrorist", "terrorism", "jihad", "extremist", "nazi", "hitler", 
    "fascist", "racist", "slurs", "hate", "slavery", "genocide", "lynching", "burning", "hanging", 
    "protest", "riot", "uprising", "coup", "holocaust", "concentration camp", "dictator", "war crimes", 
    "prison camp", "executioner", "hostage", "abuse", "rape", "incest", "molest", "pedophile", "child", 
    "minor", "underage", "toddler", "infant", "baby", "trafficking", "kidnapping", "exploitation", 
    "nude", "naked", "topless", "bottomless", "sex", "erotic", "porn", "pornography", "hentai", "xxx", 
    "fetish", "bdsm", "dominatrix", "bondage", "dildo", "vibrator", "intercourse", "orgasm", 
    "ejaculation", "masturbation", "obscene", "strip", "stripping", "lingerie", "seduce", "prostitute", 
    "escort", "brothel", "incestuous", "adultery", "lust", "genitals", "penis", "vagina", "breast", 
    "nipples", "clitoris", "anus", "rectum", "oral sex", "anal sex", "bestiality", "zoophilia", 
    "necrophilia", "pedophilia", "suicide", "self-harm", "cut", "cutting", "overdose", "hang", 
    "depression", "depressed", "mental illness", "disorder", "trauma", "PTSD", "schizophrenia", 
    "bipolar", "anorexia", "bulimia", "starvation", "eating disorder", "thinspo", "self-injury", 
    "self-destruction", "jump", "fall", "drown", "asphyxiation", "choking", "suffocation", "drugs", 
    "drug", "cocaine", "heroin", "meth", "methamphetamine", "crack", "LSD", "acid", "ecstasy", "MDMA", 
    "molly", "opium", "opioid", "oxy", "fentanyl", "shrooms", "psilocybin", "cannabis", "weed", 
    "marijuana", "pot", "joint", "blunt", "bong", "smoking", "vape", "nicotine", "cigarette", "cigar", 
    "hookah", "alcohol", "beer", "wine", "vodka", "rum", "tequila", "whiskey", "absinthe", "drunk", 
    "intoxicated", "poisoning", "addict", "addiction", "trafficking", "smuggling", "cartel", "gang", 
    "mafia", "underworld", "crime", "criminal", "robbery", "theft", "burglary", "fraud", "scam", 
    "hacking", "hacker", "dark web", "deep web", "darknet", "illegal", "contraband", "counterfeit", 
    "forgery", "bribery", "corruption", "blackmail", "extortion", "mob", "gang violence", "prison", 
    "inmate", "prisoner", "jail", "convict", "execution chamber", "lethal injection", "gas chamber", 
    "electric chair", "cancer", "AIDS", "HIV", "COVID", "SARS", "Ebola", "plague", "leprosy", 
    "tuberculosis", "cholera", "malaria", "syphilis", "gonorrhea", "STD", "STI", "hepatitis", 
    "pandemic", "epidemic", "tumor", "brain damage", "organ failure", "miscarriage", "abortion", 
    "stillbirth", "deformity", "mutation", "genetic disease", "disability"
]

def generate_short_video_content(first_name, text, base_dir):
    """
    Generate short video content based on PDF text with separate files
    """
    short_video_dir = base_dir / "short video"
    short_video_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the restricted words list for reference
    with open(short_video_dir / "restricted_words.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(RESTRICTED_WORDS))
    
    prompt = f"""
    Based EXCLUSIVELY on the following information about {first_name}:
    
    {text[:MAX_TEXT_LENGTH]}
    
    Create a short YouTube Shorts/TikTok/Instagram Reels video package with the following components:
    
    1. SCRIPT: 200-word script starting with a HOOK and ending with a QUESTION asking viewers to comment
    2. DESCRIPTION: Professional video description with relevant hashtags and emojis
    3. IMAGE_PROMPTS: 2 detailed AI image generation prompts for visuals
    4. VIDEO_PROMPT: 1 detailed AI video generation prompt for a 5-second clip
    5. THUMBNAIL_PROMPT: 1 detailed AI image generation prompt specifically for a vertical thumbnail (720x1280)
    
    IMPORTANT RULES FOR VISUAL PROMPTS:
    - DO NOT include the person's name ({first_name}) in any image or video prompts (EXCEPT for the THUMBNAIL_PROMPT)
    - DO NOT include any restricted or inappropriate words (violence, weapons, explicit content, etc.)
    - Create CINEMATIC views that visually represent the content of each script section
    - Focus on symbolic, atmospheric, and environmental representations
    - Use professional cinematic language and visual storytelling techniques
    - IMAGE_PROMPT_1 should represent the FIRST third of the script conceptually
    - VIDEO_PROMPT should represent the SECOND third of the script conceptually  
    - IMAGE_PROMPT_2 should represent the FINAL third of the script conceptually
    
    SPECIAL RULE FOR THUMBNAIL_PROMPT:
    - INCLUDE the person's name ({first_name}) in the thumbnail prompt to make it personalized and engaging
    
    For image and video prompts, create detailed cinematic descriptions that include:
    - Visual atmosphere and mood
    - Camera angles and movement (for video)
    - Lighting and color palette
    - Composition and framing
    - Symbolic elements that represent the script content
    - Professional cinematic style (no personal names except for thumbnail)
    
    For the THUMBNAIL_PROMPT, create a compelling vertical thumbnail (720x1280) that:
    - Features {first_name} in a symbolic or atmospheric representation
    - Uses bold, eye-catching colors optimized for mobile viewing
    - Has a mysterious or intriguing element to drive clicks
    - Uses professional cinematic photography style with dramatic lighting
    - Includes negative space at the top or bottom for potential text overlay
    - Optimized for vertical mobile viewing
    
    Format your response EXACTLY like this:

    [SCRIPT]
    Your script content here...

    [DESCRIPTION]
    Your description content here...

    [IMAGE_PROMPT_1]
    Your first cinematic image prompt here...
    [APPEARS_AT: FIRST third of script]

    [VIDEO_PROMPT]
    Your cinematic video prompt here...
    [APPEARS_AT: SECOND third of script]

    [IMAGE_PROMPT_2]
    Your second cinematic image prompt here...
    [APPEARS_AT: FINAL third of script]

    [THUMBNAIL_PROMPT]
    Your cinematic thumbnail prompt here...
    """

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional video content creator specializing in short-form vertical content. Create cinematic, symbolic visual prompts that represent script content. For image and video prompts, avoid using personal names. For the thumbnail prompt, INCLUDE the person's name to make it personalized. Avoid any restricted/inappropriate words. Focus on atmospheric, environmental, and symbolic representations using professional cinematic language."},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=2800
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
        return True and image_success and video_success
        
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
                duration=5,
                aspect_ratio="9:16",
                timeout=600
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
        
        # Save image prompts (cleaned - remove name and restricted words)
        image_prompts = []
        for i in range(1, 3):
            start_tag = f"[IMAGE_PROMPT_{i}]"
            end_tag = f"[VIDEO_PROMPT]" if i == 1 else "[THUMBNAIL_PROMPT]"
            
            if start_tag in content and end_tag in content:
                prompt_content = content.split(start_tag)[1].split(end_tag)[0].strip()
                # Remove the [APPEARS_AT] line if present
                if "[APPEARS_AT:" in prompt_content:
                    prompt_content = prompt_content.split("[APPEARS_AT:")[0].strip()
                cleaned_prompt = clean_ai_prompt(prompt_content, first_name, remove_name=True)
                image_prompts.append(cleaned_prompt)
                
                with open(short_video_dir / f"image_prompt_{i}.txt", "w", encoding="utf-8") as f:
                    f.write(cleaned_prompt)
        
        # Save video prompt (cleaned - remove name and restricted words)
        if "[VIDEO_PROMPT]" in content and "[IMAGE_PROMPT_2]" in content:
            video_prompt = content.split("[VIDEO_PROMPT]")[1].split("[IMAGE_PROMPT_2]")[0].strip()
            # Remove the [APPEARS_AT] line if present
            if "[APPEARS_AT:" in video_prompt:
                video_prompt = video_prompt.split("[APPEARS_AT:")[0].strip()
            cleaned_video_prompt = clean_ai_prompt(video_prompt, first_name, remove_name=True)
            with open(short_video_dir / "video_prompt.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_video_prompt)
        
        # Save thumbnail prompt (cleaned - remove restricted words but KEEP the name)
        if "[THUMBNAIL_PROMPT]" in content:
            thumbnail_prompt = content.split("[THUMBNAIL_PROMPT]")[1].strip()
            cleaned_thumbnail_prompt = clean_ai_prompt(thumbnail_prompt, first_name, remove_name=False)
            with open(short_video_dir / "thumbnail_prompt.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_thumbnail_prompt)
                
    except Exception as e:
        print(f"⚠️ Error parsing video components: {e}")

def clean_ai_prompt(prompt_text, first_name, remove_name=True):
    """
    Clean the AI image prompt by removing unwanted introductory text, year references, 
    restricted words, and optionally the person's name
    """
    # Remove common introductory patterns
    patterns_to_remove = [
        "**AI Image Generation Prompt:**",
        "This prompt is designed to create",
        "capturing not just his physical likeness",
        "the essence of his legacy",
        "one of the greatest minds in history",
        "==================================================",
        "**Prompt:**",
        "Here is a detailed AI image generation prompt:",
        "Create an image of",
        "Generate a visual of",
        "Produce an image showing",
    ]
    
    cleaned_prompt = prompt_text
    for pattern in patterns_to_remove:
        cleaned_prompt = cleaned_prompt.replace(pattern, "")
    
    # Remove the person's name specifically if requested
    if remove_name:
        cleaned_prompt = cleaned_prompt.replace(first_name, "").replace(first_name.lower(), "").replace(first_name.upper(), "")
    
    # Remove specific year references
    cleaned_prompt = re.sub(r'\b(in|from|during|of|circa)\s+\d{4}s?\b', '', cleaned_prompt, flags=re.IGNORECASE)
    cleaned_prompt = re.sub(r'\b\d{4}s?\b', '', cleaned_prompt)
    
    # Remove any restricted words
    for restricted_word in RESTRICTED_WORDS:
        # Use regex to match whole words only
        cleaned_prompt = re.sub(r'\b' + restricted_word + r'\b', '', cleaned_prompt, flags=re.IGNORECASE)
    
    # Remove any phrases that start with creation verbs
    if re.match(r'^(Create|Generate|Make|Design|Produce)\s+(a|an|the)?\s+', cleaned_prompt, re.IGNORECASE):
        cleaned_prompt = re.sub(r'^(Create|Generate|Make|Design|Produce)\s+(a|an|the)?\s*', '', cleaned_prompt, flags=re.IGNORECASE)
    
    # Remove any double newlines and clean up whitespace
    cleaned_prompt = "\n".join([line.strip() for line in cleaned_prompt.split("\n") if line.strip()])
    cleaned_prompt = re.sub(r'\s+', ' ', cleaned_prompt)  # Remove extra spaces
    cleaned_prompt = cleaned_prompt.strip()
    
    # Ensure the prompt starts with descriptive content, not commands
    if cleaned_prompt.startswith(('a ', 'an ', 'the ')):
        cleaned_prompt = cleaned_prompt[0].upper() + cleaned_prompt[1:]
    
    return cleaned_prompt
