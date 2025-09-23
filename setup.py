#!/usr/bin/env python3
"""
Setup script for SpotifytoUG dependencies.
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("=== SpotifytoUG Setup ===\n")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Virtual environment detected")
    else:
        print("⚠️  Warning: Not in a virtual environment. Consider creating one:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print()
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return 1
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browsers"):
        return 1
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n⚠️  Configuration file .env not found")
        print("Copying .env.example to .env...")
        try:
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✓ .env file created from .env.example")
            print("\n📝 Please edit .env file and add your credentials:")
            print("   - Spotify API credentials (client ID, client secret)")
            print("   - Ultimate Guitar username and password")
            print("   - Spotify playlist ID to sync")
        except Exception as e:
            print(f"✗ Failed to create .env file: {e}")
            return 1
    else:
        print("✓ .env file already exists")
    
    print("\n=== Setup Complete ===")
    print("Next steps:")
    print("1. Edit .env file with your credentials")
    print("2. Run: python main.py --preview")
    print("3. Run: python main.py --sync")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())