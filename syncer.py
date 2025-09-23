"""
Main synchronization module for SpotifytoUG.
"""
import asyncio
import logging
from typing import List, Dict, Tuple
from config import Config
from spotify_client import SpotifyClient
from ug_client import UltimateGuitarClient

logger = logging.getLogger(__name__)


class PlaylistSyncer:
    """Main class for synchronizing Spotify playlists to Ultimate Guitar."""
    
    def __init__(self, config: Config):
        """
        Initialize the syncer with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.spotify_client = None
        self.ug_client = None
        
    def _initialize_spotify_client(self):
        """Initialize Spotify client."""
        if not self.spotify_client:
            self.spotify_client = SpotifyClient(
                client_id=self.config.spotify_client_id,
                client_secret=self.config.spotify_client_secret,
                redirect_uri=self.config.spotify_redirect_uri
            )
            
    async def sync_playlist(self, target_playlist_name: str = None) -> bool:
        """
        Sync a Spotify playlist to Ultimate Guitar.
        
        Args:
            target_playlist_name: Name for the UG playlist (defaults to Spotify playlist name)
            
        Returns:
            True if sync successful, False otherwise
        """
        try:
            logger.info("Starting playlist synchronization")
            
            # Initialize Spotify client
            self._initialize_spotify_client()
            
            # Get Spotify playlist info and tracks
            logger.info(f"Fetching Spotify playlist: {self.config.spotify_playlist_id}")
            playlist_info = self.spotify_client.get_playlist_info(self.config.spotify_playlist_id)
            tracks = self.spotify_client.get_playlist_tracks(self.config.spotify_playlist_id)
            
            logger.info(f"Found {len(tracks)} tracks in playlist '{playlist_info['name']}'")
            
            # Use provided name or default to Spotify playlist name
            ug_playlist_name = target_playlist_name or playlist_info['name']
            
            # Connect to Ultimate Guitar
            async with UltimateGuitarClient(
                username=self.config.ug_username,
                password=self.config.ug_password,
                headless=self.config.headless_browser
            ) as ug_client:
                
                # Login to UG
                if not await ug_client.login():
                    logger.error("Failed to login to Ultimate Guitar")
                    return False
                
                # Check if playlist already exists
                existing_playlists = await ug_client.get_existing_playlists()
                
                if ug_playlist_name not in existing_playlists:
                    # Create new playlist
                    logger.info(f"Creating new playlist: {ug_playlist_name}")
                    if not await ug_client.create_playlist(
                        playlist_name=ug_playlist_name,
                        description=f"Synced from Spotify playlist: {playlist_info['name']}"
                    ):
                        logger.error("Failed to create playlist on Ultimate Guitar")
                        return False
                else:
                    logger.info(f"Using existing playlist: {ug_playlist_name}")
                
                # Add tracks to UG playlist
                successful_adds = 0
                failed_adds = 0
                
                for i, track in enumerate(tracks, 1):
                    logger.info(f"Processing track {i}/{len(tracks)}: {track['name']} by {track['artist']}")
                    
                    try:
                        success = await ug_client.search_and_add_song(
                            song_name=track['name'],
                            artist_name=track['artist'],
                            playlist_name=ug_playlist_name
                        )
                        
                        if success:
                            successful_adds += 1
                        else:
                            failed_adds += 1
                            logger.warning(f"Failed to add: {track['name']} by {track['artist']}")
                            
                        # Add delay between requests to be respectful
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        failed_adds += 1
                        logger.error(f"Error adding track {track['name']}: {e}")
                
                # Report results
                total_tracks = len(tracks)
                logger.info(f"Sync completed: {successful_adds}/{total_tracks} tracks added successfully")
                if failed_adds > 0:
                    logger.warning(f"{failed_adds} tracks failed to sync")
                
                return successful_adds > 0
                
        except Exception as e:
            logger.error(f"Error during playlist sync: {e}")
            return False
            
    async def get_spotify_playlist_info(self) -> Dict:
        """
        Get information about the configured Spotify playlist.
        
        Returns:
            Dictionary with playlist information
        """
        try:
            self._initialize_spotify_client()
            return self.spotify_client.get_playlist_info(self.config.spotify_playlist_id)
        except Exception as e:
            logger.error(f"Error fetching Spotify playlist info: {e}")
            return {}
            
    async def preview_sync(self) -> Tuple[Dict, List[Dict]]:
        """
        Preview what tracks would be synced without actually syncing.
        
        Returns:
            Tuple of (playlist_info, tracks_list)
        """
        try:
            self._initialize_spotify_client()
            
            playlist_info = self.spotify_client.get_playlist_info(self.config.spotify_playlist_id)
            tracks = self.spotify_client.get_playlist_tracks(self.config.spotify_playlist_id)
            
            logger.info(f"Preview: {len(tracks)} tracks would be synced from '{playlist_info['name']}'")
            
            return playlist_info, tracks
            
        except Exception as e:
            logger.error(f"Error during preview: {e}")
            return {}, []