# install_dependencies.py
import subprocess
import sys
from pathlib import Path

def install_requirements(requirements_file="requirements.txt"):
    """Install all packages listed in requirements.txt"""
    requirements_path = Path(requirements_file)

    if not requirements_path.exists():
        print(f"❌ {requirements_file} not found!")
        sys.exit(1)

    print(f"📦 Installing packages from {requirements_file}...\n")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
        print("\n🎉 All packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install some packages.")

if __name__ == "__main__":
    install_requirements()
