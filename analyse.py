import csv
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

CSV_FILE = "playlist.csv"


def load_tracks(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plot_by_year(tracks: list[dict], ax: plt.Axes):
    years = [int(t["year"]) for t in tracks]
    year_counts = Counter(years)
    sorted_years = sorted(year_counts)
    ax.bar(sorted_years, [year_counts[y] for y in sorted_years], color="steelblue", width=0.8)
    ax.set_title("Tracks by Release Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of tracks")
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.tick_params(axis="x", rotation=45)


def plot_by_decade(tracks: list[dict], ax: plt.Axes):
    decades = [t["decade"] for t in tracks]
    decade_counts = Counter(decades)
    labels = [f"{d}s" for d in sorted(decade_counts)]
    values = [decade_counts[d] for d in sorted(decade_counts)]
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.set_title("Tracks by Decade")


def plot_top_genres(tracks: list[dict], ax: plt.Axes, top_n: int = 20):
    genre_counts: Counter = Counter()
    for t in tracks:
        for genre in t["genres"].split("; "):
            genre = genre.strip()
            if genre:
                genre_counts[genre] += 1

    top = genre_counts.most_common(top_n)
    if not top:
        ax.set_title("Genre data unavailable")
        return

    labels, values = zip(*top)
    ax.barh(list(reversed(labels)), list(reversed(values)), color="coral")
    ax.set_title(f"Top {top_n} Genres")
    ax.set_xlabel("Number of tracks")


def plot_top_artists(tracks: list[dict], ax: plt.Axes, top_n: int = 15):
    artist_counts: Counter = Counter()
    for t in tracks:
        for artist in t["artists"].split("; "):
            artist = artist.strip()
            if artist:
                artist_counts[artist] += 1

    top = artist_counts.most_common(top_n)
    labels, values = zip(*top)
    ax.barh(list(reversed(labels)), list(reversed(values)), color="mediumseagreen")
    ax.set_title(f"Top {top_n} Artists by Track Count")
    ax.set_xlabel("Number of tracks")


def plot_popularity_distribution(tracks: list[dict], ax: plt.Axes):
    pops = [int(t["popularity"]) for t in tracks if t["popularity"]]
    ax.hist(pops, bins=20, color="mediumpurple", edgecolor="white")
    ax.set_title("Popularity Distribution")
    ax.set_xlabel("Popularity score (0–100)")
    ax.set_ylabel("Number of tracks")


def plot_duration_distribution(tracks: list[dict], ax: plt.Axes):
    durations = [int(t["duration_ms"]) / 60000 for t in tracks if t["duration_ms"]]
    ax.hist(durations, bins=30, color="goldenrod", edgecolor="white")
    ax.set_title("Track Duration Distribution")
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Number of tracks")
    ax.axvline(sum(durations) / len(durations), color="red", linestyle="--", label=f"Mean: {sum(durations)/len(durations):.1f} min")
    ax.legend()


def print_summary(tracks: list[dict]):
    years = [int(t["year"]) for t in tracks]
    pops = [int(t["popularity"]) for t in tracks if t["popularity"]]
    durations = [int(t["duration_ms"]) / 60000 for t in tracks if t["duration_ms"]]
    explicit = sum(1 for t in tracks if t["explicit"].lower() == "true")

    print(f"Total tracks:        {len(tracks)}")
    print(f"Year range:          {min(years)}–{max(years)}")
    print(f"Avg popularity:      {sum(pops)/len(pops):.1f}/100")
    print(f"Avg duration:        {sum(durations)/len(durations):.2f} min")
    print(f"Explicit tracks:     {explicit} ({explicit/len(tracks)*100:.1f}%)")

    print("\nTop 10 artists:")
    artist_counts: Counter = Counter()
    for t in tracks:
        for a in t["artists"].split("; "):
            if a.strip():
                artist_counts[a.strip()] += 1
    for artist, count in artist_counts.most_common(10):
        print(f"  {count:>3}x  {artist}")

    print("\nTop 10 genres:")
    genre_counts: Counter = Counter()
    for t in tracks:
        for g in t["genres"].split("; "):
            if g.strip():
                genre_counts[g.strip()] += 1
    for genre, count in genre_counts.most_common(10):
        print(f"  {count:>3}x  {genre}")

    print("\nDecade breakdown:")
    decade_counts = Counter(t["decade"] for t in tracks)
    for decade in sorted(decade_counts):
        bar = "#" * (decade_counts[decade] // 3)
        print(f"  {decade}s: {decade_counts[decade]:>3}  {bar}")


def main():
    tracks = load_tracks(CSV_FILE)
    print_summary(tracks)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Spotify Playlist Analysis", fontsize=16, fontweight="bold")

    plot_by_year(tracks, axes[0, 0])
    plot_by_decade(tracks, axes[0, 1])
    plot_top_genres(tracks, axes[0, 2])
    plot_top_artists(tracks, axes[1, 0])
    plot_popularity_distribution(tracks, axes[1, 1])
    plot_duration_distribution(tracks, axes[1, 2])

    plt.tight_layout()
    plt.savefig("analysis.png", dpi=150)
    print("\nChart saved to analysis.png")
    plt.show()


if __name__ == "__main__":
    main()
