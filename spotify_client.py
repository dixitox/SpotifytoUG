"""
Spotify API integration module for fetching playlist data.
"""
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SpotifyClient:
    """Client for interacting with Spotify API."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """Initialize Spotify client with credentials."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Set up OAuth scope for reading playlists
        scope = "playlist-read-private playlist-read-collaborative"
        
        # Initialize Spotify client
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        ))
        
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """
        Fetch all tracks from a Spotify playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            List of track information dictionaries
        """
        try:
            tracks = []
            results = self.sp.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['type'] == 'track':
                        track_info = {
                            'name': item['track']['name'],
                            'artist': ', '.join([artist['name'] for artist in item['track']['artists']]),
                            'album': item['track']['album']['name'],
                            'spotify_id': item['track']['id'],
                            'external_urls': item['track']['external_urls']
                        }
                        tracks.append(track_info)
                
                # Get next batch if available
                results = self.sp.next(results) if results['next'] else None
                
            logger.info(f"Successfully fetched {len(tracks)} tracks from playlist {playlist_id}")
            return tracks
            
        except Exception as e:
            logger.error(f"Error fetching playlist tracks: {e}")
            raise
    
    def get_playlist_info(self, playlist_id: str) -> Dict:
        """
        Get basic information about a playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            Dictionary with playlist information
        """
        try:
            playlist = self.sp.playlist(playlist_id)
            return {
                'name': playlist['name'],
                'description': playlist['description'],
                'total_tracks': playlist['tracks']['total'],
                'owner': playlist['owner']['display_name'],
                'external_urls': playlist['external_urls']
            }
        except Exception as e:
            logger.error(f"Error fetching playlist info: {e}")
            raise
            
    def search_track(self, track_name: str, artist_name: str) -> Optional[Dict]:
        """
        Search for a track on Spotify.
        
        Args:
            track_name: Name of the track
            artist_name: Name of the artist
            
        Returns:
            Track information if found, None otherwise
        """
        try:
            query = f"track:{track_name} artist:{artist_name}"
            results = self.sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                return {
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'spotify_id': track['id'],
                    'external_urls': track['external_urls']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error searching for track: {e}")
            return None