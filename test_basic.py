"""
Simple tests for SpotifytoUG modules.
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from spotify_client import SpotifyClient


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def test_config_validation_missing_vars(self):
        """Test that config validation fails when required vars are missing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# Empty config file\n")
            temp_env_file = f.name
        
        try:
            config = Config(env_file=temp_env_file)
            self.assertFalse(config.validate())
        finally:
            os.unlink(temp_env_file)
    
    def test_config_validation_with_vars(self):
        """Test that config validation passes when all vars are present."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("""
SPOTIFY_CLIENT_ID=test_id
SPOTIFY_CLIENT_SECRET=test_secret
SPOTIFY_PLAYLIST_ID=test_playlist
UG_USERNAME=test_user
UG_PASSWORD=test_pass
""")
            temp_env_file = f.name
        
        try:
            config = Config(env_file=temp_env_file)
            self.assertTrue(config.validate())
            self.assertEqual(config.spotify_client_id, 'test_id')
            self.assertEqual(config.ug_username, 'test_user')
        finally:
            os.unlink(temp_env_file)


class TestSpotifyClient(unittest.TestCase):
    """Test Spotify client functionality."""
    
    def test_spotify_client_initialization(self):
        """Test that SpotifyClient can be initialized."""
        # Mock spotipy to avoid actual API calls
        with patch('spotify_client.spotipy.Spotify') as mock_spotify:
            client = SpotifyClient(
                client_id='test_id',
                client_secret='test_secret',
                redirect_uri='http://localhost:8080/callback'
            )
            
            self.assertEqual(client.client_id, 'test_id')
            self.assertEqual(client.client_secret, 'test_secret')
            mock_spotify.assert_called_once()
    
    def test_track_info_parsing(self):
        """Test that track information is parsed correctly."""
        with patch('spotify_client.spotipy.Spotify') as mock_spotify:
            # Create mock track data
            mock_track_data = {
                'items': [{
                    'track': {
                        'type': 'track',
                        'name': 'Test Song',
                        'id': 'test_id',
                        'artists': [{'name': 'Test Artist'}],
                        'album': {'name': 'Test Album'},
                        'external_urls': {'spotify': 'http://test.url'}
                    }
                }],
                'next': None
            }
            
            mock_spotify_instance = MagicMock()
            mock_spotify_instance.playlist_tracks.return_value = mock_track_data
            mock_spotify.return_value = mock_spotify_instance
            
            client = SpotifyClient('test_id', 'test_secret', 'test_uri')
            tracks = client.get_playlist_tracks('test_playlist_id')
            
            self.assertEqual(len(tracks), 1)
            self.assertEqual(tracks[0]['name'], 'Test Song')
            self.assertEqual(tracks[0]['artist'], 'Test Artist')
            self.assertEqual(tracks[0]['album'], 'Test Album')


if __name__ == '__main__':
    unittest.main()