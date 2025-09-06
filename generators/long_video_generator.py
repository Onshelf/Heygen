# generators/long_video_generator.py
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

def generate_long_video_content(first_name, text, base_dir):
    """
    Generate professional long video content based on PDF text with separate files
    """
    long_video_dir = base_dir / "long video"
    long_video_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the restricted words list for reference
    with open(long_video_dir / "restricted_words.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(RESTRICTED_WORDS))
    
    # Generate the main script first
    script_prompt = f"""
Based EXCLUSIVELY on the following information about {first_name}:

{text[:MAX_TEXT_LENGTH]}

Create a 3000-word professional documentary script that includes:
- Engaging introduction that starts immediately with content
- Comprehensive coverage of the subject's life and achievements
- Natural transitions between topics
- Professional narration style
- Strong conclusion with call to action

SPECIFIC REQUIREMENTS:
1. The script must be divided into 14 equal conceptual sections that flow naturally
2. Section 1 (Introduction) must end with: "I'm Habeeb — this is Visioneers. Subscribe and stay inspired."
3. When mentioning time periods, use only centuries or parts of centuries (e.g., "early 20th century", "mid-1800s") — NEVER use full specific dates like "1947" or "January 15, 1929"
4. Focus on the subject's adult life and professional achievements
5. Avoid detailing childhood family scenes

Format the script with clear section markers like [SECTION 1], [SECTION 2], etc.
"""

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an award-winning documentary filmmaker. Create professional, engaging scripts that focus on adult achievements. Use only centuries or parts of centuries for time references, never full dates. Ensure section 1 ends with the exact phrase: 'I'm Habeeb — this is Visioneers. Subscribe and stay inspired.'"},
                {"role": "user", "content": script_prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=4000
        )
        
        script_content = response.choices[0].message.content.strip()
        
        # Save the script
        with open(long_video_dir / "script.txt", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        # Extract section content for more targeted visual prompts
        section_contents = extract_section_contents(script_content)
        
        # Generate 14 visual prompts (10 images + 4 videos) with specific section arrangement
        visual_prompts = generate_visual_prompts(first_name, text, section_contents, long_video_dir)
        
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
        print(f"📝 Script and 14 visual prompts (10 images + 4 videos) saved")
        return True and image_success and video_success
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        return False

def extract_section_contents(script_content):
    """
    Extract the content of each section from the script for more targeted visual prompts
    """
    section_contents = {}
    
    # Try to extract sections based on common patterns
    section_patterns = [
        r'\[SECTION (\d+)\](.*?)(?=\[SECTION \d+\]|$)',
        r'Section (\d+):(.*?)(?=Section \d+:|$)',
        r'Part (\d+):(.*?)(?=Part \d+:|$)',
        r'### Section (\d+) ###(.*?)(?=### Section \d+ ###|$)'
    ]
    
    for pattern in section_patterns:
        matches = re.findall(pattern, script_content, re.DOTALL | re.IGNORECASE)
        if matches:
            for match in matches:
                section_num = int(match[0])
                section_content = match[1].strip()
                section_contents[section_num] = section_content
            break
    
    # If no sections found, split the script into 14 equal parts
    if not section_contents:
        lines = script_content.split('\n')
        lines_per_section = max(1, len(lines) // 14)
        for i in range(1, 15):
            start_idx = (i-1) * lines_per_section
            end_idx = i * lines_per_section if i < 14 else len(lines)
            section_content = '\n'.join(lines[start_idx:end_idx]).strip()
            section_contents[i] = section_content
    
    return section_contents

def generate_visual_prompts(first_name, text, section_contents, long_video_dir):
    """
    Generate 14 visual prompts (10 images + 4 videos) with specific section arrangement
    Sections 1,2,4,5,7,8,10,11,13,14: Image prompts
    Sections 3,6,9,12: Video prompts
    Each prompt is specifically tailored to its section content
    """
    visual_prompts = []
    
    for section in range(1, 15):
        section_content = section_contents.get(section, "")
        
        if section in [1, 2, 4, 5, 7, 8, 10, 11, 13, 14]:  # Image sections
            prompt_type = "image"
            prompt = f"""
Based EXCLUSIVELY on the content of SECTION {section} from this documentary script:

{section_content}

Create a detailed professional AI image generation prompt that visually represents THIS SPECIFIC SECTION.

The prompt must include:
- Visual elements that directly relate to the content of section {section}
- Setting and background context appropriate for this section's themes
- Cinematic style and artistic direction matching the section's tone
- Professional lighting and mood specifications
- Camera angle and composition suitable for documentary

SPECIFIC REQUIREMENTS:
- Create a visual representation that captures the essence of section {section}
- Focus on symbolic, atmospheric representations rather than literal depictions
- DO NOT include the person's name in the prompt
- DO NOT include any restricted or inappropriate words
- Use professional cinematic language

Make it comprehensive and suitable for AI image models.
"""
        else:  # Video sections (3, 6, 9, 12)
            prompt_type = "video"
            prompt = f"""
Based EXCLUSIVELY on the content of SECTION {section} from this documentary script:

{section_content}

Create a detailed professional AI video generation prompt that visually represents THIS SPECIFIC SECTION.

The prompt must include:
- Visual elements that directly relate to the content of section {section}
- Camera movement and angles appropriate for this section's content
- Cinematic lighting and atmosphere matching the section's tone
- Professional style and mood suitable for documentary
- Composition and framing

SPECIFIC REQUIREMENTS:
- Create a visual representation that captures the essence of section {section}
- Focus on symbolic, atmospheric representations rather than literal depictions
- DO NOT include the person's name in the prompt
- DO NOT include any restricted or inappropriate words
- Create a 5-second cinematic clip

Make it suitable for AI video models.
"""

        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": f"You are an expert at creating detailed AI {prompt_type} generation prompts for specific documentary sections. Create cinematic, symbolic prompts that directly represent the given section content without using personal names or restricted words."},
                    {"role": "user", "content": prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=600 if prompt_type == "image" else 500
            )
            
            prompt_content = response.choices[0].message.content.strip()
            cleaned_prompt = clean_ai_prompt(prompt_content, first_name, remove_name=True)
            visual_prompts.append(cleaned_prompt)
            
            # Save each cleaned prompt to separate file
            if prompt_type == "image":
                with open(long_video_dir / f"image_prompt_{section}.txt", "w", encoding="utf-8") as f:
                    f.write(cleaned_prompt)
            else:
                with open(long_video_dir / f"video_prompt_{section}.txt", "w", encoding="utf-8") as f:
                    f.write(cleaned_prompt)
                    
        except Exception as e:
            print(f"❌ Error generating {prompt_type} prompt for section {section}: {e}")
            visual_prompts.append("")
    
    return visual_prompts

def generate_ai_videos_from_prompts(long_video_dir):
    """
    Generate AI videos from the video prompt files in the long video directory
    Uses 5-second duration and 16:9 aspect ratio for documentary-style content
    """
    try:
        video_success = True
        
        # Video sections: 3, 6, 9, 12
        video_sections = [3, 6, 9, 12]
        
        for section in video_sections:
            video_prompt_file = long_video_dir / f"video_prompt_{section}.txt"
            
            if video_prompt_file.exists():
                print(f"🎬 Generating AI video for section {section} from prompt...")
                
                # Read the video prompt
                with open(video_prompt_file, "r", encoding="utf-8") as f:
                    video_prompt = f.read().strip()
                
                if not video_prompt:
                    print(f"❌ Video prompt for section {section} is empty")
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
                    with open(long_video_dir / f"video_url_{section}.txt", "w", encoding="utf-8") as f:
                        f.write(video_url)
                    
                    print(f"✅ AI video for section {section} generated successfully!")
                    
                except VideoGenerationError as e:
                    print(f"❌ AI video for section {section} generation failed: {e}")
                    video_success = False
                except Exception as e:
                    print(f"❌ Unexpected error generating AI video for section {section}: {e}")
                    video_success = False
            else:
                print(f"❌ Video prompt file for section {section} not found")
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
        return clean_ai_prompt(prompt_content, first_name, remove_name=False)  # Keep name for thumbnail
        
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
        
        # Image sections: 1, 2, 4, 5, 7, 8, 10, 11, 13, 14
        image_sections = [1, 2, 4, 5, 7, 8, 10, 11, 13, 14]
        
        for section in image_sections:
            prompt_file = long_video_dir / f"image_prompt_{section}.txt"
            
            if prompt_file.exists():
                print(f"🖼️ Generating AI image for section {section} from prompt...")
                
                # Use documentary format (1280x720) for long video content
                success, image_path, error = generate_image_from_prompt_file(
                    prompt_file, 
                    long_video_dir, 
                    width=1280, 
                    height=720, 
                    image_name=f"long_video_image_{section}.jpg"
                )
                
                if success:
                    print(f"✅ AI image for section {section} generated successfully!")
                else:
                    print(f"❌ AI image for section {section} generation failed: {error}")
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

def clean_ai_prompt(prompt_text, first_name, remove_name=True):
    """
    Clean the AI image prompt by removing unwanted introductory text, year references, 
    restricted words, and optionally the person's name
    """
    # Remove common introductory patterns
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
    
    # Remove specific year references (including full dates)
    cleaned_prompt = re.sub(r'\b\d{1,2}(st|nd|rd|th)?\s+(century|Century)\b', '', cleaned_prompt, flags=re.IGNORECASE)
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
