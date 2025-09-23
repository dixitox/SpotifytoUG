"""
Configuration management for SpotifytoUG.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for managing environment variables and settings."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Optional path to .env file
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
            
        # Spotify API settings
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.spotify_redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8080/callback')
        self.spotify_playlist_id = os.getenv('SPOTIFY_PLAYLIST_ID')
        
        # Ultimate Guitar settings
        self.ug_username = os.getenv('UG_USERNAME')
        self.ug_password = os.getenv('UG_PASSWORD')
        
        # Application settings
        self.headless_browser = os.getenv('HEADLESS_BROWSER', 'True').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_fields = [
            ('SPOTIFY_CLIENT_ID', self.spotify_client_id),
            ('SPOTIFY_CLIENT_SECRET', self.spotify_client_secret),
            ('SPOTIFY_PLAYLIST_ID', self.spotify_playlist_id),
            ('UG_USERNAME', self.ug_username),
            ('UG_PASSWORD', self.ug_password),
        ]
        
        missing_fields = []
        for field_name, field_value in required_fields:
            if not field_value:
                missing_fields.append(field_name)
                
        if missing_fields:
            logger.error(f"Missing required configuration: {', '.join(missing_fields)}")
            logger.error("Please set these environment variables or add them to your .env file")
            return False
            
        return True
        
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    def __str__(self) -> str:
        """String representation of configuration (without sensitive data)."""
        return f"""Configuration:
  Spotify Playlist ID: {self.spotify_playlist_id}
  UG Username: {self.ug_username}
  Headless Browser: {self.headless_browser}
  Log Level: {self.log_level}
  Spotify Client ID: {'***' if self.spotify_client_id else 'Not set'}
  Spotify Client Secret: {'***' if self.spotify_client_secret else 'Not set'}
  UG Password: {'***' if self.ug_password else 'Not set'}"""