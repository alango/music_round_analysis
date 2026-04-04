# Music Round Analysis

Spotify playlist analysis tool. Fetches track and artist data from the Spotify API, saves to CSV, and generates an interactive HTML dashboard.

## Setup

```bash
pip install requests matplotlib
```

Set your Spotify API credentials (from [developer.spotify.com](https://developer.spotify.com/dashboard)):

```bash
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
```

Or create a `.env` file (never commit this):
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

## Usage

```bash
# 1. Fetch playlist data → playlist.csv
python fetch_playlist.py

# 2. Generate static dashboard → index.html
python build_webpage.py

# 3. (Optional) Generate matplotlib charts
python analyse.py
```

The playlist ID is set in `fetch_playlist.py` — change `PLAYLIST_ID` to analyse a different playlist.

## GitHub Pages

`index.html` is a self-contained static page (uses Plotly CDN). To host it, enable GitHub Pages in the repo settings and set the source to the root of the main branch.
