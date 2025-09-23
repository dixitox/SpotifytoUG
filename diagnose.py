#!/usr/bin/env python3
"""
Diagnostic script for SpotifytoUG - Check setup and troubleshoot issues.
"""
import os
import sys
import asyncio
import logging
from config import Config

# Suppress logs for cleaner output
logging.basicConfig(level=logging.CRITICAL)


async def check_spotify_connection(config):
    """Test Spotify API connection."""
    try:
        from spotify_client import SpotifyClient
        
        print("🎵 Testing Spotify API connection...")
        client = SpotifyClient(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret,
            redirect_uri=config.spotify_redirect_uri
        )
        
        # Try to get user info as a basic connectivity test
        user = client.sp.current_user()
        if user:
            print(f"✓ Connected to Spotify as: {user.get('display_name', user.get('id', 'Unknown'))}")
            
            # Test playlist access
            try:
                playlist_info = client.get_playlist_info(config.spotify_playlist_id)
                print(f"✓ Can access playlist: '{playlist_info['name']}' ({playlist_info['total_tracks']} tracks)")
                return True
            except Exception as e:
                print(f"✗ Cannot access playlist {config.spotify_playlist_id}: {e}")
                print("  Check that the playlist ID is correct and accessible")
                return False
        else:
            print("✗ Could not authenticate with Spotify")
            return False
            
    except Exception as e:
        print(f"✗ Spotify connection failed: {e}")
        print("  Check your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        return False


async def check_ug_connection(config):
    """Test Ultimate Guitar connection."""
    try:
        from ug_client import UltimateGuitarClient
        
        print("\n🎸 Testing Ultimate Guitar connection...")
        
        # Check if playwright browsers are installed
        try:
            from playwright.async_api import async_playwright
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            await browser.close()
            await playwright.stop()
            print("✓ Playwright browsers are installed")
        except Exception as e:
            print(f"✗ Playwright browsers not properly installed: {e}")
            print("  Run: playwright install chromium")
            return False
        
        # Test UG login (this might take a moment)
        print("  Attempting login to Ultimate Guitar...")
        async with UltimateGuitarClient(
            username=config.ug_username,
            password=config.ug_password,
            headless=True
        ) as ug_client:
            
            login_success = await ug_client.login()
            if login_success:
                print("✓ Successfully logged into Ultimate Guitar")
                
                # Test getting existing playlists
                try:
                    playlists = await ug_client.get_existing_playlists()
                    print(f"✓ Found {len(playlists)} existing playlists")
                    if playlists:
                        print(f"  Examples: {', '.join(playlists[:3])}")
                    return True
                except Exception as e:
                    print(f"⚠️  Login successful but couldn't fetch playlists: {e}")
                    return True  # Login worked, which is the main thing
            else:
                print("✗ Failed to login to Ultimate Guitar")
                print("  Check your UG_USERNAME and UG_PASSWORD")
                print("  Make sure your account is not locked or requires 2FA")
                return False
                
    except Exception as e:
        print(f"✗ Ultimate Guitar connection failed: {e}")
        return False


def check_dependencies():
    """Check that all required dependencies are installed."""
    print("📦 Checking dependencies...")
    
    required_modules = [
        'spotipy',
        'playwright',
        'dotenv',
        'requests'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nMissing modules: {', '.join(missing_modules)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_config_file():
    """Check configuration file."""
    print("\n⚙️  Checking configuration...")
    
    if not os.path.exists('.env'):
        print("✗ .env file not found")
        print("  Copy .env.example to .env and fill in your credentials")
        return False
    else:
        print("✓ .env file exists")
    
    try:
        config = Config()
        if config.validate():
            print("✓ All required configuration variables are set")
            return config
        else:
            print("✗ Some required configuration variables are missing")
            return None
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        return None


async def main():
    """Main diagnostic function."""
    print("=== SpotifytoUG Diagnostic Tool ===\n")
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing modules.")
        return 1
    
    # Check configuration
    config = check_config_file()
    if not config:
        print("\n❌ Configuration check failed. Please fix your .env file.")
        return 1
    
    # Test connections
    spotify_ok = await check_spotify_connection(config)
    ug_ok = await check_ug_connection(config)
    
    print("\n" + "="*50)
    if spotify_ok and ug_ok:
        print("🎉 All checks passed! Your setup is ready to sync playlists.")
        print("\nNext steps:")
        print("  python main.py --preview   # Preview tracks")
        print("  python main.py --sync      # Sync playlist")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above before syncing.")
        if not spotify_ok:
            print("\n🎵 Spotify issues:")
            print("  - Check your Spotify API credentials")
            print("  - Ensure your app has the correct redirect URI")
            print("  - Verify playlist ID is correct and accessible")
        
        if not ug_ok:
            print("\n🎸 Ultimate Guitar issues:")
            print("  - Check your UG username and password")
            print("  - Ensure Playwright browsers are installed")
            print("  - Check if your account requires 2FA (not supported)")
        
        return 1


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error during diagnostics: {e}")
        sys.exit(1)