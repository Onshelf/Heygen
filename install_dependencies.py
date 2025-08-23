# install_dependencies.py
import subprocess
import sys

def install_packages():
    """Install all required packages"""
    packages = [
        "pandas",
        "openpyxl",
        "wikipedia-api",
        "requests",
        "PyPDF2",
        "openai==0.28"
    ]
    
    print("📦 Installing required packages...")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    print("🎉 All packages installed successfully!")

if __name__ == "__main__":
    install_packages()
