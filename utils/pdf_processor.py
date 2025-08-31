# utils/pdf_processor.py
import pypdf
from pathlib import Path
from typing import Optional
import logging

class PDFProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text, or None if extraction fails
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text_parts = []
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                text = "\n".join(text_parts)
                self.logger.info(f"✅ Text extracted from PDF ({len(text)} characters)")
                return text
                
        except pypdf.PdfException as e:
            self.logger.error(f"PDF processing error for {pdf_path.name}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing {pdf_path.name}: {e}")
            
        return None

# Standalone function for convenience
def extract_text_from_pdf(pdf_path: str | Path) -> Optional[str]:
    """
    Extract text from PDF file
    
    Args:
        pdf_path: Path to the PDF file (string or Path object)
        
    Returns:
        Extracted text, or None if extraction fails
    """
    processor = PDFProcessor()
    return processor.extract_text_from_pdf(Path(pdf_path))
