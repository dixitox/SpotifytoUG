# SpotifytoUG Development Instructions

SpotifytoUG is a Python automation tool that syncs Spotify playlists to Ultimate Guitar using Playwright browser automation and the Spotify Web API.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup (NEVER CANCEL - Build may take 15-30 minutes)
- Create virtual environment: `python -m venv venv`
- Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt` -- takes 2-5 minutes normally. NEVER CANCEL. Set timeout to 15+ minutes.
  - **NETWORK ISSUES**: pip install may fail with timeout errors due to network connectivity. Retry 2-3 times if this occurs.
  - If repeated failures: `pip install --timeout 600 -r requirements.txt`
- Install Playwright browsers: `python -m playwright install chromium` -- takes 10-25 minutes and may fail due to network issues. NEVER CANCEL. Set timeout to 45+ minutes.
  - **BROWSER INSTALL FAILURES**: Common due to large downloads. If fails, retry: `python -m playwright install`
  - Alternative if browsers fail: `python -m playwright install chromium --with-deps` (requires sudo access)
- Copy configuration: `cp .env.example .env`
- Run setup script: `python setup.py` -- automates the above steps, takes 15-30 minutes total. NEVER CANCEL. Set timeout to 45+ minutes.
  - **IMPORTANT**: setup.py may fail on browser installation but continue with other steps. This is normal.

### Testing and Validation
- Run unit tests: `python test_basic.py` -- takes <5 seconds
- No pytest required - uses built-in unittest framework
- No linting tools configured (no flake8, black, etc.)
- Validate setup: `python diagnose.py` -- checks dependencies, config, and API connections. May hang if credentials are invalid.

### Running the Application
- ALWAYS run the bootstrapping steps first
- Check setup: `python diagnose.py` -- NEVER CANCEL, may take 2-5 minutes for API timeouts
- Preview sync: `python main.py --preview` -- shows what would be synced without making changes
- Sync playlist: `python main.py --sync` -- performs actual synchronization
- Custom playlist name: `python main.py --sync --name "My Guitar Songs"`
- Visible browser mode: `python main.py --sync --visible` -- useful for debugging
- Headless mode: `python main.py --sync --headless` -- explicitly run browser hidden
- Custom config: `python main.py --config .env.custom` -- use different config file
- Show help: `python main.py --help`

### Available Command Line Options
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

## Validation Scenarios

**CRITICAL**: Always manually validate functionality after making changes. Simply starting the application is NOT sufficient.

### Required Manual Testing Steps
1. **Setup Validation**: Run `python diagnose.py` and verify all checks pass (dependencies, config file existence, basic module imports)
2. **Preview Mode Testing**: Run `python main.py --preview` with valid Spotify credentials and verify it displays track list
3. **Configuration Testing**: Test with missing .env file, invalid credentials, and valid credentials
4. **Help System Testing**: Verify `python main.py --help` shows proper usage information

### Expected Timing and Behavior
- **NEVER CANCEL**: Setup takes 15-30 minutes total due to Playwright browser downloads
- **NEVER CANCEL**: Initial diagnose.py run may take 2-5 minutes for API timeouts with invalid credentials
- Unit tests complete in <5 seconds
- Preview mode should complete in 30-60 seconds with valid credentials
- Full sync timing depends on playlist size (1-5 minutes per 50 songs)

## Configuration Requirements

The application requires a `.env` file with specific credentials:

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

- Copy `.env.example` to `.env` first
- Get Spotify credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
- Playlist ID is found in Spotify URLs: `https://open.spotify.com/playlist/[ID_HERE]`
- Ultimate Guitar account must not have 2FA enabled

## Common Development Tasks

### File Structure and Key Components
```
├── main.py              # Main CLI application entry point
├── setup.py             # Automated setup script
├── diagnose.py          # Setup validation and troubleshooting
├── config.py            # Configuration management
├── spotify_client.py    # Spotify API integration
├── ug_client.py         # Ultimate Guitar browser automation
├── syncer.py            # Main synchronization logic
├── test_basic.py        # Unit tests
├── requirements.txt     # Python dependencies
├── .env.example         # Configuration template
└── .env                 # Your actual configuration (create from .env.example)
```

### Key Dependencies and Versions
- Python 3.7+ required
- spotipy==2.23.0 (Spotify Web API)
- playwright==1.40.0 (Browser automation)
- python-dotenv==1.0.0 (Environment management)
- requests==2.31.0 (HTTP requests)

### Making Changes
- Always test configuration validation: modify `config.py` then run `python test_basic.py`
- For Spotify integration changes: test with `python main.py --preview`
- For UG automation changes: test with visible browser `python main.py --sync --visible`
- Always run diagnostic after changes: `python diagnose.py`

### Troubleshooting Common Issues
- **Playwright install fails**: Network timeouts are common. Retry 2-3 times or use `--with-deps` flag
- **pip install timeouts**: Common in restricted networks. Use `pip install --timeout 600 -r requirements.txt` and retry
- **Diagnose script hangs**: Usually due to invalid Spotify credentials trying to connect to API
- **UG login fails**: Check username/password and ensure no 2FA is enabled
- **Dependencies missing**: Re-run `pip install -r requirements.txt`
- **Module not found errors**: Ensure virtual environment is activated
- **Network connectivity issues**: Many operations require internet access and may fail in restricted environments

## Important Notes
- **Browser automation is core functionality** - Playwright browsers MUST be installed for the app to work
- **No CI/CD configured** - no GitHub workflows, no automated testing beyond local unit tests
- **Network dependency** - Application requires internet access for both Spotify API and Ultimate Guitar
- **Credentials required** - Application will not work without valid Spotify Developer credentials and UG account
- **Rate limiting** - Built-in delays respect Ultimate Guitar's servers (don't modify these)

## Development Environment
- Supports Linux, macOS, and Windows
- Requires Chrome/Chromium browser (installed by Playwright)
- Virtual environment strongly recommended
- No IDE-specific configuration files
- No linting/formatting tools configured