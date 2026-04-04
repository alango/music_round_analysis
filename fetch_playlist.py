import csv
import os
import requests

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
PLAYLIST_ID = "2cL8wiLXmsMEDCoJ7PjPJI"
OUTPUT_CSV = "playlist.csv"


def get_access_token(client_id: str, client_secret: str) -> str:
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_playlist_tracks(token: str, playlist_id: str) -> list[dict]:
    tracks = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}

    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        tracks.extend(data["items"])
        url = data.get("next")

    return tracks


def get_artist_genres(token: str, artist_ids: list[str]) -> dict[str, list[str]]:
    """Fetch genres for artists in batches of 50."""
    genres = {}
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i : i + 50]
        response = requests.get(
            "https://api.spotify.com/v1/artists",
            headers=headers,
            params={"ids": ",".join(batch)},
        )
        response.raise_for_status()
        for artist in response.json()["artists"]:
            if artist:
                genres[artist["id"]] = artist.get("genres", [])

    return genres


def main():
    print("Fetching access token...")
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    print(f"Fetching playlist {PLAYLIST_ID}...")
    items = get_playlist_tracks(token, PLAYLIST_ID)

    # Collect unique artist IDs
    artist_ids = list(
        {
            artist["id"]
            for item in items
            if item.get("track")
            for artist in item["track"]["artists"]
            if artist.get("id")
        }
    )

    print(f"Fetching genres for {len(artist_ids)} artists...")
    artist_genres = get_artist_genres(token, artist_ids)

    rows = []
    for item in items:
        track = item.get("track")
        if not track:
            continue

        name = track["name"]
        artists = [a["name"] for a in track["artists"]]
        artist_ids_track = [a["id"] for a in track["artists"] if a.get("id")]

        release_date = track["album"]["release_date"]
        year = int(release_date[:4])
        decade = (year // 10) * 10

        # Merge genres from all artists on the track, deduplicated
        genres = list(
            dict.fromkeys(
                g for aid in artist_ids_track for g in artist_genres.get(aid, [])
            )
        )

        rows.append(
            {
                "track_name": name,
                "artists": "; ".join(artists),
                "year": year,
                "decade": decade,
                "genres": "; ".join(genres),
                "popularity": track.get("popularity", ""),
                "duration_ms": track.get("duration_ms", ""),
                "explicit": track.get("explicit", False),
            }
        )

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} tracks to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
