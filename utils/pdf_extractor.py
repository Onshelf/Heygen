# utils/pdf_extractor.py
import PyPDF2
import requests
import os
from pathlib import Path

def download_wikipedia_pdf(first_name, output_dir="/content/Output"):
    """
    Download Wikipedia PDF for the given name and extract text
    """
    try:
        # Create output directory
        base_dir = Path(output_dir)
        main_folder = base_dir / first_name
        main_folder.mkdir(parents=True, exist_ok=True)
        
        # Generate Wikipedia PDF URL
        pdf_url = f"https://en.wikipedia.org/api/rest_v1/page/pdf/{first_name.replace(' ', '_')}"
        
        # Download PDF
        response = requests.get(pdf_url)
        
        if response.status_code == 200:
            pdf_path = main_folder / f"{first_name}.pdf"
            
            # Save PDF
            with open(pdf_path, 'wb') as file:
                file.write(response.content)
            
            print(f"✅ PDF downloaded successfully: {pdf_path}")
            
            # Extract text from PDF
            text = extract_text_from_pdf(pdf_path)
            return text
            
        else:
            print(f"❌ Failed to download PDF. HTTP Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading PDF: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF file
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
            
            print(f"✅ Text extracted from PDF ({len(text)} characters)")
            return text
            
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return None
