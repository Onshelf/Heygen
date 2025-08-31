# main.py - Clean main controller
import os
from pathlib import Path

# Import from separate modules
from config.settings import BASE_DIR, EXCEL_FILE_PATH, EXCEL_SHEET_NAME
from utils.api_config import setup_openai_api
from utils.excel_reader import read_excel_names
from utils.pdf_downloader import download_wikipedia_pdf
from utils.pdf_processor import extract_text_from_pdf
from generators.youtube_post_generator import generate_youtube_post
from generators.short_video_generator import generate_short_video_content
from generators.long_video_generator import generate_long_video_content

def setup_directories(first_name):
    """
    Create all necessary directories
    """
    base_dir = BASE_DIR / first_name
    directories = [
        base_dir / "post",
        base_dir / "short video",
        base_dir / "long video"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully")
    return base_dir

def main():
    """
    Main function to run the complete pipeline
    """
    print("🚀 Starting Complete Content Generation Pipeline")
    print("=" * 60)
    
    # Step 1: Setup API
    print("🔑 Step 1: Configuring API...")
    if not setup_openai_api():
        print("❌ Cannot proceed without valid API configuration.")
        return
    
    print("\n" + "=" * 60)
    
    # Step 2: Read name from Excel
    print("📊 Step 2: Reading name from Excel file...")
    first_name = read_excel_names(EXCEL_FILE_PATH, EXCEL_SHEET_NAME)
    
    if not first_name:
        print("❌ Cannot proceed without a valid name.")
        return
    
    print("\n" + "=" * 60)
    
    # Step 3: Download PDF
    print("📄 Step 3: Downloading Wikipedia PDF...")
    try:
        pdf_path = download_wikipedia_pdf(first_name, BASE_DIR)
        print(f"✅ PDF downloaded: {pdf_path}")
    except Exception as e:
        print(f"❌ Failed to download PDF: {e}")
        return
    
    print("\n" + "=" * 60)
    
    # Step 4: Extract text from PDF
    print("📖 Step 4: Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print("❌ Cannot proceed without extracted PDF content.")
        return
    
    print(f"✅ Text extracted ({len(text)} characters)")
    
    print("\n" + "=" * 60)
    
    # Step 5: Setup directories
    print("📁 Step 5: Creating directories...")
    base_dir = setup_directories(first_name)
    
    print("\n" + "=" * 60)
    
    # Step 6: Generate content
    print("🎬 Step 6: Generating content...")
    
    success1 = generate_youtube_post(first_name, text, base_dir)
    print()
    
    success2 = generate_short_video_content(first_name, text, base_dir)
    print()
    
    success3 = generate_long_video_content(first_name, text, base_dir)
    print()
    
    # Final Summary
    print("📊 Final Summary:")
    print("=" * 60)
    print(f"📝 Name Processed: {first_name}")
    print(f"📄 PDF Content: ✅ Extracted ({len(text)} characters)")
    print(f"📱 YouTube Post: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"🎥 Short Video: {'✅ Success' if success2 else '❌ Failed'}")
    print(f"🎬 Long Video: {'✅ Success' if success3 else '❌ Failed'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 All content generated successfully!")
        print(f"📁 Files saved in: {base_dir}/")
    else:
        print("\n⚠️  Some content generation failed.")

if __name__ == "__main__":
    main()
