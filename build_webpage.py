import csv
import json
from collections import Counter, defaultdict

CSV_FILE = "playlist.csv"
OUTPUT_HTML = "index.html"


def load_tracks(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


MAX_HOVER_TRACKS = 30


def track_label(t: dict) -> str:
    return f"{t['track_name']} - {t['artists']}"


def hover_text(track_list: list[str]) -> str:
    if len(track_list) <= MAX_HOVER_TRACKS:
        return "<br>".join(track_list)
    shown = "<br>".join(track_list[:MAX_HOVER_TRACKS])
    return f"{shown}<br>... and {len(track_list) - MAX_HOVER_TRACKS} more"


def build_year_data(tracks: list[dict]) -> dict:
    by_year: defaultdict[int, list[str]] = defaultdict(list)
    for t in tracks:
        by_year[int(t["year"])].append(track_label(t))
    years = sorted(by_year)
    return {
        "x": years,
        "y": [len(by_year[y]) for y in years],
        "text": [hover_text(by_year[y]) for y in years],
    }


def build_decade_data(tracks: list[dict]) -> dict:
    by_decade: defaultdict[str, list[str]] = defaultdict(list)
    for t in tracks:
        by_decade[t["decade"]].append(track_label(t))
    decades = sorted(by_decade, key=int)
    labels = [f"{d}s" for d in decades]
    return {
        "labels": labels,
        "values": [len(by_decade[d]) for d in decades],
        "text": [hover_text(by_decade[d]) for d in decades],
    }


def build_genre_data(tracks: list[dict], top_n: int = 20) -> dict:
    by_genre: defaultdict[str, list[str]] = defaultdict(list)
    for t in tracks:
        for g in t["genres"].split("; "):
            g = g.strip()
            if g:
                by_genre[g].append(track_label(t))
    top = sorted(by_genre, key=lambda g: len(by_genre[g]), reverse=True)[:top_n]
    top = list(reversed(top))
    return {
        "y": top,
        "x": [len(by_genre[g]) for g in top],
        "text": [hover_text(by_genre[g]) for g in top],
    }


def build_artist_data(tracks: list[dict], top_n: int = 15) -> dict:
    by_artist: defaultdict[str, list[str]] = defaultdict(list)
    for t in tracks:
        for a in t["artists"].split("; "):
            a = a.strip()
            if a:
                by_artist[a].append(track_label(t))
    top = sorted(by_artist, key=lambda a: len(by_artist[a]), reverse=True)[:top_n]
    top = list(reversed(top))
    return {
        "y": top,
        "x": [len(by_artist[a]) for a in top],
        "text": [hover_text(by_artist[a]) for a in top],
    }


def build_popularity_data(tracks: list[dict]) -> dict:
    buckets: defaultdict[int, list[str]] = defaultdict(list)
    for t in tracks:
        if t["popularity"]:
            bucket = (int(t["popularity"]) // 5) * 5
            buckets[bucket].append(track_label(t))
    sorted_buckets = sorted(buckets)
    return {
        "x": list(sorted_buckets),
        "ticktext": [f"{b}-{b+4}" for b in sorted_buckets],
        "y": [len(buckets[b]) for b in sorted_buckets],
        "text": [hover_text(buckets[b]) for b in sorted_buckets],
    }


def main():
    tracks = load_tracks(CSV_FILE)

    data = {
        "year": build_year_data(tracks),
        "decade": build_decade_data(tracks),
        "genre": build_genre_data(tracks),
        "artist": build_artist_data(tracks),
        "popularity": build_popularity_data(tracks),
        "total": len(tracks),
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Playlist Analysis</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f1117;
      color: #e0e0e0;
      padding: 24px;
    }}
    h1 {{
      text-align: center;
      font-size: 1.8rem;
      font-weight: 600;
      margin-bottom: 6px;
      color: #fff;
    }}
    .subtitle {{
      text-align: center;
      color: #888;
      margin-bottom: 28px;
      font-size: 0.95rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      max-width: 1400px;
      margin: 0 auto;
    }}
    .chart-box {{
      background: #1a1d27;
      border-radius: 12px;
      padding: 16px;
      border: 1px solid #2a2d3a;
    }}
    .chart-box.wide {{
      grid-column: 1 / -1;
    }}
    h2 {{
      font-size: 0.95rem;
      font-weight: 500;
      color: #aaa;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .chart {{ width: 100%; }}
  </style>
</head>
<body>
  <h1>Spotify Playlist Analysis</h1>
  <p class="subtitle">{data["total"]} tracks</p>

  <div class="grid">
    <div class="chart-box wide">
      <h2>Tracks by Release Year</h2>
      <div id="chart-year" class="chart"></div>
    </div>
    <div class="chart-box">
      <h2>Tracks by Decade</h2>
      <div id="chart-decade" class="chart"></div>
    </div>
    <div class="chart-box">
      <h2>Popularity Distribution</h2>
      <div id="chart-popularity" class="chart"></div>
    </div>
    <div class="chart-box">
      <h2>Top 20 Genres</h2>
      <div id="chart-genre" class="chart"></div>
    </div>
    <div class="chart-box">
      <h2>Top 15 Artists</h2>
      <div id="chart-artist" class="chart"></div>
    </div>
  </div>

<script>
const DATA = {json.dumps(data)};

const darkLayout = {{
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: {{ color: "#ccc", size: 12 }},
  margin: {{ t: 10, r: 10, b: 50, l: 50 }},
  xaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a" }},
  yaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a" }},
  hoverlabel: {{
    bgcolor: "#1e2130",
    bordercolor: "#444",
    font: {{ color: "#eee", size: 11 }},
    align: "left",
  }},
}};

const config = {{ responsive: true, displayModeBar: false }};

// --- Year chart ---
Plotly.newPlot("chart-year", [{{
  type: "bar",
  x: DATA.year.x,
  y: DATA.year.y,
  hovertext: DATA.year.text,
  hovertemplate: "<b>%{{x}}</b> — %{{y}} tracks<br><br>%{{hovertext}}<extra></extra>",
  marker: {{ color: "#4e9af1" }},
}}], {{
  ...darkLayout,
  margin: {{ t: 10, r: 10, b: 40, l: 40 }},
  bargap: 0.2,
}}, config);

// --- Decade pie ---
Plotly.newPlot("chart-decade", [{{
  type: "pie",
  labels: DATA.decade.labels,
  values: DATA.decade.values,
  hovertext: DATA.decade.text,
  hovertemplate: "<b>%{{label}}</b><br>%{{value}} tracks (%{{percent}})<br><br>%{{hovertext}}<extra></extra>",
  textinfo: "label+percent",
  hole: 0.35,
  marker: {{
    colors: ["#e07b54","#e0b454","#7be07b","#54b4e0","#a07be0","#e07ba0","#7be0d4","#e0e07b"],
  }},
}}], {{
  ...darkLayout,
  margin: {{ t: 10, r: 10, b: 10, l: 10 }},
  showlegend: false,
}}, config);

// --- Popularity histogram ---
Plotly.newPlot("chart-popularity", [{{
  type: "bar",
  x: DATA.popularity.x,
  y: DATA.popularity.y,
  hovertext: DATA.popularity.text,
  hovertemplate: "<b>Score %{{x}}</b> — %{{y}} tracks<br><br>%{{hovertext}}<extra></extra>",
  marker: {{ color: "#a07be0" }},
}}], {{
  ...darkLayout,
  xaxis: {{
    gridcolor: "#2a2d3a",
    zerolinecolor: "#2a2d3a",
    tickmode: "array",
    tickvals: DATA.popularity.x,
    ticktext: DATA.popularity.ticktext,
    title: {{ text: "Popularity score", font: {{ size: 11 }} }},
  }},
  yaxis: {{
    gridcolor: "#2a2d3a",
    zerolinecolor: "#2a2d3a",
    title: {{ text: "Tracks", font: {{ size: 11 }} }},
  }},
}}, config);

// --- Genre bar ---
Plotly.newPlot("chart-genre", [{{
  type: "bar",
  orientation: "h",
  y: DATA.genre.y,
  x: DATA.genre.x,
  hovertext: DATA.genre.text,
  hovertemplate: "<b>%{{y}}</b> — %{{x}} tracks<br><br>%{{hovertext}}<extra></extra>",
  marker: {{ color: "#e07b7b" }},
}}], {{
  ...darkLayout,
  margin: {{ t: 10, r: 20, b: 40, l: 130 }},
  height: 480,
  xaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a", title: {{ text: "Tracks", font: {{ size: 11 }} }} }},
  yaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a", automargin: true }},
}}, config);

// --- Artist bar ---
Plotly.newPlot("chart-artist", [{{
  type: "bar",
  orientation: "h",
  y: DATA.artist.y,
  x: DATA.artist.x,
  hovertext: DATA.artist.text,
  hovertemplate: "<b>%{{y}}</b> — %{{x}} tracks<br><br>%{{hovertext}}<extra></extra>",
  marker: {{ color: "#54e0a0" }},
}}], {{
  ...darkLayout,
  margin: {{ t: 10, r: 20, b: 40, l: 150 }},
  height: 480,
  xaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a", title: {{ text: "Tracks", font: {{ size: 11 }} }} }},
  yaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a", automargin: true }},
}}, config);
</script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Saved {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
