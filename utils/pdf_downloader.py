# utils/pdf_downloader.py
from pathlib import Path
import requests
from urllib.parse import quote
import logging
import time

class PDFDownloader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def download_wikipedia_pdf(self, figure_name: str, save_path: Path, timeout: int = 30) -> Path:
        """
        Downloads Wikipedia page as PDF with proper headers
        """
        base_url = "https://en.wikipedia.org/api/rest_v1/page/pdf/"
        encoded_name = quote(figure_name.replace(' ', '_'))  # Use underscores for Wikipedia format
        pdf_url = f"{base_url}{encoded_name}"
        
        output_path = save_path / figure_name / f"{figure_name.replace(' ', '_')}.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Add delay to avoid rate limiting
            time.sleep(1)
            
            response = requests.get(pdf_url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
                
            self.logger.info(f"✅ PDF downloaded successfully: {output_path}")
            return output_path
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                self.logger.error(f"❌ Access forbidden. Wikipedia may be blocking automated requests.")
                self.logger.error(f"   Try: 1) Using a different IP 2) Adding delays 3) Using a proxy")
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to download PDF for {figure_name}: {str(e)}")
            raise

# Alternative method using web scraping fallback
def download_wikipedia_pdf(figure_name: str, save_path: Path, timeout: int = 30) -> Path:
    """
    Main download function with fallback options
    """
    downloader = PDFDownloader()
    return downloader.download_wikipedia_pdf(figure_name, save_path, timeout)
