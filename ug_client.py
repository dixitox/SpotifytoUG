"""
Ultimate Guitar automation module using Playwright.
"""
import asyncio
import logging
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)


class UltimateGuitarClient:
    """Client for automating Ultimate Guitar website interactions."""
    
    def __init__(self, username: str, password: str, headless: bool = True):
        """Initialize UG client with credentials."""
        self.username = username
        self.password = password
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_browser()
        
    async def start_browser(self):
        """Start the Playwright browser."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.page = await self.browser.new_page()
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            raise
            
    async def close_browser(self):
        """Close the browser and cleanup."""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            
    async def login(self) -> bool:
        """
        Login to Ultimate Guitar.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Attempting to login to Ultimate Guitar")
            await self.page.goto("https://www.ultimate-guitar.com/user/signin")
            
            # Wait for login form to load
            await self.page.wait_for_selector("input[name='username']", timeout=10000)
            
            # Fill login form
            await self.page.fill("input[name='username']", self.username)
            await self.page.fill("input[name='password']", self.password)
            
            # Submit form
            await self.page.click("button[type='submit']")
            
            # Wait for either successful login or error
            try:
                # Wait for profile menu to appear (indicates successful login)
                await self.page.wait_for_selector(".js-header-user-menu", timeout=10000)
                logger.info("Successfully logged in to Ultimate Guitar")
                return True
            except:
                # Check for error message
                error_element = await self.page.query_selector(".error-message")
                if error_element:
                    error_text = await error_element.text_content()
                    logger.error(f"Login failed: {error_text}")
                else:
                    logger.error("Login failed: Unknown error")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
            
    async def create_playlist(self, playlist_name: str, description: str = "") -> bool:
        """
        Create a new playlist on Ultimate Guitar.
        
        Args:
            playlist_name: Name of the playlist
            description: Optional description
            
        Returns:
            True if playlist created successfully, False otherwise
        """
        try:
            logger.info(f"Creating playlist: {playlist_name}")
            
            # Navigate to playlists page
            await self.page.goto("https://www.ultimate-guitar.com/user/playlists")
            
            # Look for create playlist button
            create_button = await self.page.query_selector("a[href*='create']")
            if not create_button:
                # Try alternative selector
                create_button = await self.page.query_selector(".btn-create-playlist")
                
            if create_button:
                await create_button.click()
            else:
                # If no create button found, try the plus icon or similar
                await self.page.click(".fa-plus, .icon-plus, [data-action='create']")
            
            # Wait for create form
            await self.page.wait_for_selector("input[name='name'], input[placeholder*='name']", timeout=10000)
            
            # Fill playlist form
            await self.page.fill("input[name='name'], input[placeholder*='name']", playlist_name)
            
            # Fill description if field exists
            desc_field = await self.page.query_selector("textarea[name='description'], textarea[placeholder*='description']")
            if desc_field and description:
                await desc_field.fill(description)
            
            # Submit form
            await self.page.click("button[type='submit'], .btn-save, .btn-create")
            
            # Wait for success indicator or redirect
            await self.page.wait_for_timeout(2000)
            
            logger.info(f"Playlist '{playlist_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            return False
            
    async def search_and_add_song(self, song_name: str, artist_name: str, playlist_name: str) -> bool:
        """
        Search for a song and add it to a playlist.
        
        Args:
            song_name: Name of the song
            artist_name: Name of the artist
            playlist_name: Name of the playlist to add to
            
        Returns:
            True if song added successfully, False otherwise
        """
        try:
            logger.info(f"Searching for: {song_name} by {artist_name}")
            
            # Navigate to search page
            search_query = f"{song_name} {artist_name}".strip()
            await self.page.goto(f"https://www.ultimate-guitar.com/search.php?search_type=title&value={search_query}")
            
            # Wait for search results
            await self.page.wait_for_selector(".js-search-results, .search-results", timeout=10000)
            
            # Look for the first relevant result
            first_result = await self.page.query_selector(".js-search-results .js-click-track, .search-results a")
            
            if first_result:
                # Click on the first result
                await first_result.click()
                
                # Wait for song page to load
                await self.page.wait_for_timeout(2000)
                
                # Look for "Add to playlist" button
                add_button = await self.page.query_selector(".js-add-to-playlist, .btn-add-playlist, [data-action*='playlist']")
                
                if add_button:
                    await add_button.click()
                    
                    # Wait for playlist selection modal
                    await self.page.wait_for_selector(".playlist-modal, .modal-playlist", timeout=5000)
                    
                    # Select the target playlist
                    playlist_option = await self.page.query_selector(f"[data-playlist-name='{playlist_name}'], .playlist-item:has-text('{playlist_name}')")
                    
                    if playlist_option:
                        await playlist_option.click()
                        logger.info(f"Added '{song_name}' by '{artist_name}' to playlist '{playlist_name}'")
                        return True
                    else:
                        logger.warning(f"Playlist '{playlist_name}' not found in selection")
                        return False
                else:
                    logger.warning("Add to playlist button not found")
                    return False
            else:
                logger.warning(f"No search results found for '{song_name}' by '{artist_name}'")
                return False
                
        except Exception as e:
            logger.error(f"Error adding song to playlist: {e}")
            return False
            
    async def get_existing_playlists(self) -> List[str]:
        """
        Get list of existing playlists for the user.
        
        Returns:
            List of playlist names
        """
        try:
            await self.page.goto("https://www.ultimate-guitar.com/user/playlists")
            
            # Wait for playlists to load
            await self.page.wait_for_selector(".playlist-item, .user-playlist", timeout=10000)
            
            # Extract playlist names
            playlist_elements = await self.page.query_selector_all(".playlist-name, .playlist-title")
            playlists = []
            
            for element in playlist_elements:
                name = await element.text_content()
                if name:
                    playlists.append(name.strip())
                    
            logger.info(f"Found {len(playlists)} existing playlists")
            return playlists
            
        except Exception as e:
            logger.error(f"Error fetching existing playlists: {e}")
            return []