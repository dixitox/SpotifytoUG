#!/usr/bin/env python3
"""
Main script for SpotifytoUG - Sync Spotify playlists to Ultimate Guitar.
"""
import asyncio
import argparse
import sys
import logging
from config import Config
from syncer import PlaylistSyncer

logger = logging.getLogger(__name__)


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Sync Spotify playlists to Ultimate Guitar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --sync                    # Sync the configured playlist
  python main.py --preview                 # Preview tracks without syncing
  python main.py --sync --name "My UG Playlist"  # Sync with custom UG playlist name
  python main.py --config .env.custom     # Use custom config file
        """
    )
    
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Sync the Spotify playlist to Ultimate Guitar'
    )
    
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview tracks that would be synced (no actual sync)'
    )
    
    parser.add_argument(
        '--name',
        type=str,
        help='Custom name for the Ultimate Guitar playlist'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (default: .env)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (overrides config)'
    )
    
    parser.add_argument(
        '--visible',
        action='store_true',
        help='Run browser in visible mode (overrides config)'
    )
    
    args = parser.parse_args()
    
    # If no action specified, show help
    if not args.sync and not args.preview:
        parser.print_help()
        return 1
    
    try:
        # Load configuration
        config = Config(env_file=args.config)
        
        # Override headless setting if specified
        if args.headless:
            config.headless_browser = True
        elif args.visible:
            config.headless_browser = False
        
        # Setup logging
        config.setup_logging()
        
        # Validate configuration
        if not config.validate():
            logger.error("Configuration validation failed")
            logger.info("Please copy .env.example to .env and fill in your credentials")
            return 1
        
        logger.info("Configuration loaded successfully")
        logger.debug(str(config))
        
        # Initialize syncer
        syncer = PlaylistSyncer(config)
        
        if args.preview:
            # Preview mode
            logger.info("Running in preview mode")
            playlist_info, tracks = await syncer.preview_sync()
            
            if playlist_info and tracks:
                print(f"\n=== Preview: Spotify Playlist '{playlist_info['name']}' ===")
                print(f"Description: {playlist_info.get('description', 'No description')}")
                print(f"Owner: {playlist_info['owner']}")
                print(f"Total tracks: {len(tracks)}")
                print(f"\nTracks to be synced:")
                
                for i, track in enumerate(tracks, 1):
                    print(f"  {i:3d}. {track['name']} - {track['artist']}")
                    
                print(f"\nTarget UG playlist name: {args.name or playlist_info['name']}")
                print("Note: This was a preview. Use --sync to actually sync the playlist.")
            else:
                logger.error("Failed to preview playlist")
                return 1
                
        elif args.sync:
            # Sync mode
            logger.info("Starting synchronization")
            
            success = await syncer.sync_playlist(target_playlist_name=args.name)
            
            if success:
                logger.info("Synchronization completed successfully!")
                return 0
            else:
                logger.error("Synchronization failed")
                return 1
                
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug("Error details:", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))