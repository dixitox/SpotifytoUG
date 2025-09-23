# SpotifytoUG

A Python tool to sync Spotify playlists to Ultimate Guitar website using Playwright automation and the Spotify Web API.

## Features

- 🎵 Fetch tracks from any Spotify playlist using the official Spotify API
- 🎸 Automatically search and add songs to Ultimate Guitar playlists
- 🔄 Smart playlist synchronization with error handling
- 🤖 Browser automation using Playwright for Ultimate Guitar interactions
- 📋 Preview mode to see what tracks would be synced before running
- ⚙️ Configurable settings via environment variables
- 📝 Comprehensive logging for monitoring sync progress

## Prerequisites

- Python 3.7 or higher
- Spotify Developer Account (for API access)
- Ultimate Guitar account
- Chrome/Chromium browser (installed automatically by Playwright)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dixitox/SpotifytoUG.git
   cd SpotifytoUG
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Run the setup script:**
   ```bash
   python setup.py
   ```

   This will:
   - Install all Python dependencies
   - Install Playwright browsers
   - Create a `.env` configuration file

## Configuration

### Spotify API Setup

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app
3. Note your Client ID and Client Secret
4. Add `http://localhost:8080/callback` to your app's redirect URIs

### Environment Variables

Edit the `.env` file with your credentials:

```bash
# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8080/callback

# Ultimate Guitar Credentials
UG_USERNAME=your_ug_username
UG_PASSWORD=your_ug_password

# Playlist Configuration
SPOTIFY_PLAYLIST_ID=your_spotify_playlist_id
```

### Finding Your Spotify Playlist ID

The playlist ID is in the Spotify URL:
```
https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
                                  ^^^^^^^^^^^^^^^^^^^
                                  This is your playlist ID
```

## Usage

### Preview Mode (Recommended First Step)

Preview what tracks would be synced without making any changes:

```bash
python main.py --preview
```

### Sync Playlist

Sync your Spotify playlist to Ultimate Guitar:

```bash
python main.py --sync
```

### Custom Playlist Name

Sync with a custom name for the Ultimate Guitar playlist:

```bash
python main.py --sync --name "My Guitar Songs"
```

### Browser Visibility

Run with visible browser window (useful for debugging):

```bash
python main.py --sync --visible
```

## Command Line Options

```
usage: main.py [-h] [--sync] [--preview] [--name NAME] [--config CONFIG] [--headless] [--visible]

Sync Spotify playlists to Ultimate Guitar

options:
  -h, --help       show this help message and exit
  --sync           Sync the Spotify playlist to Ultimate Guitar
  --preview        Preview tracks that would be synced (no actual sync)
  --name NAME      Custom name for the Ultimate Guitar playlist
  --config CONFIG  Path to configuration file (default: .env)
  --headless       Run browser in headless mode (overrides config)
  --visible        Run browser in visible mode (overrides config)
```

## How It Works

1. **Authentication**: 
   - Connects to Spotify API using OAuth2 flow
   - Logs into Ultimate Guitar using provided credentials

2. **Data Fetching**: 
   - Retrieves all tracks from the specified Spotify playlist
   - Extracts song names, artists, and metadata

3. **Playlist Creation**: 
   - Creates a new playlist on Ultimate Guitar (if it doesn't exist)
   - Uses the Spotify playlist name or your custom name

4. **Song Matching**: 
   - Searches Ultimate Guitar for each song
   - Adds found songs to the target playlist
   - Logs any songs that couldn't be found

## Troubleshooting

### Common Issues

**"Login failed" error:**
- Check your Ultimate Guitar username and password
- Ensure your account is active and not locked

**"No search results found" errors:**
- Some songs may not be available on Ultimate Guitar
- Song names might not match exactly between platforms
- The tool will log which songs couldn't be found

**Browser automation failures:**
- Ultimate Guitar's website structure may change
- Run with `--visible` to see what's happening
- Check the logs for specific error messages

### Logging

The tool provides detailed logging. Set the log level in your `.env` file:

```bash
LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for personal use only. Please respect:
- Spotify's API terms of service
- Ultimate Guitar's terms of service
- Copyright laws and artist rights
- Rate limits and be respectful to both services

The tool includes delays between requests to be respectful to the Ultimate Guitar servers.