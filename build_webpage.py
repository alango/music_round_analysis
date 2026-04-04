import csv
import json
from collections import Counter, defaultdict

CSV_FILE = "playlist.csv"
OUTPUT_HTML = "index.html"


def load_tracks(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def track_label(t: dict) -> str:
    return f"{t['track_name']} - {t['artists']}"


def hover_text(track_list: list[str]) -> str:
    return "<br>".join(track_list)


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
    @media (max-width: 700px) {{
      body {{ padding: 12px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .chart-box.wide {{ grid-column: 1; }}
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
    .tap-hint {{
      font-size: 0.75rem;
      color: #555;
      margin-top: 4px;
    }}

    /* Track panel */
    #track-panel {{
      display: none;
      position: fixed;
      bottom: 0; left: 0; right: 0;
      background: #1a1d27;
      border-top: 1px solid #3a3d4a;
      border-radius: 16px 16px 0 0;
      max-height: 55vh;
      z-index: 1000;
      box-shadow: 0 -4px 24px rgba(0,0,0,0.5);
      display: none;
      flex-direction: column;
    }}
    #track-panel.open {{ display: flex; }}
    #track-panel-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 18px 10px;
      border-bottom: 1px solid #2a2d3a;
      flex-shrink: 0;
    }}
    #track-panel-title {{
      font-weight: 600;
      font-size: 0.95rem;
      color: #fff;
    }}
    #track-panel-close {{
      background: none;
      border: none;
      color: #888;
      font-size: 1.2rem;
      cursor: pointer;
      padding: 0 4px;
      line-height: 1;
    }}
    #track-panel-close:hover {{ color: #fff; }}
    #track-panel-list {{
      overflow-y: auto;
      padding: 10px 18px 20px;
      font-size: 0.85rem;
      line-height: 1.7;
      color: #ccc;
    }}
    #track-panel-list .track {{ padding: 2px 0; border-bottom: 1px solid #222; }}
    #track-panel-list .track:last-child {{ border-bottom: none; }}
    #track-panel-list .more {{ color: #666; font-style: italic; padding-top: 6px; }}

    #panel-backdrop {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.4);
      z-index: 999;
    }}
    #panel-backdrop.open {{ display: block; }}
  </style>
</head>
<body>
  <h1>Spotify Playlist Analysis</h1>
  <p class="subtitle">{data["total"]} tracks</p>

  <div class="grid">
    <div class="chart-box wide">
      <h2>Tracks by Release Year</h2>
      <div id="chart-year" class="chart"></div>
      <p class="tap-hint">Tap / click a bar to see tracks</p>
    </div>
    <div class="chart-box">
      <h2>Popularity Distribution</h2>
      <div id="chart-popularity" class="chart"></div>
      <p class="tap-hint">Tap / click a bar to see tracks</p>
    </div>
    <div class="chart-box">
      <h2>Top 20 Genres</h2>
      <div id="chart-genre" class="chart"></div>
      <p class="tap-hint">Tap / click a bar to see tracks</p>
    </div>
    <div class="chart-box">
      <h2>Top 15 Artists</h2>
      <div id="chart-artist" class="chart"></div>
      <p class="tap-hint">Tap / click a bar to see tracks</p>
    </div>
  </div>

  <div id="panel-backdrop"></div>
  <div id="track-panel">
    <div id="track-panel-header">
      <span id="track-panel-title"></span>
      <button id="track-panel-close">&#x2715;</button>
    </div>
    <div id="track-panel-list"></div>
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
  }},
}};

const config = {{ responsive: true, displayModeBar: false }};

// --- Track panel ---
function openPanel(title, trackText) {{
  document.getElementById("track-panel-title").textContent = title;
  const list = document.getElementById("track-panel-list");
  list.innerHTML = "";
  const parts = trackText.split("<br>");
  parts.forEach(line => {{
    const div = document.createElement("div");
    div.className = line.startsWith("...") ? "more" : "track";
    div.textContent = line;
    list.appendChild(div);
  }});
  document.getElementById("track-panel").classList.add("open");
  document.getElementById("panel-backdrop").classList.add("open");
}}

function closePanel() {{
  document.getElementById("track-panel").classList.remove("open");
  document.getElementById("panel-backdrop").classList.remove("open");
}}

document.getElementById("track-panel-close").addEventListener("click", closePanel);
document.getElementById("panel-backdrop").addEventListener("click", closePanel);

// Map each chart div to its label and text arrays
const chartMeta = {{
  "chart-year":       {{ labels: DATA.year.x,             texts: DATA.year.text,        fmt: v => `${{v}}` }},
"chart-popularity": {{ labels: DATA.popularity.ticktext, texts: DATA.popularity.text,  fmt: v => `Score ${{v}}` }},
  "chart-genre":      {{ labels: DATA.genre.y,             texts: DATA.genre.text,       fmt: v => v }},
  "chart-artist":     {{ labels: DATA.artist.y,            texts: DATA.artist.text,      fmt: v => v }},
}};

function wireClick(divId) {{
  const el = document.getElementById(divId);
  const meta = chartMeta[divId];
  el.on("plotly_click", function(eventData) {{
    const pt = eventData.points[0];
    const idx = pt.pointIndex;
    openPanel(meta.fmt(meta.labels[idx]), meta.texts[idx]);
  }});
}}

// --- Year chart ---
Plotly.newPlot("chart-year", [{{
  type: "bar",
  x: DATA.year.x,
  y: DATA.year.y,
  hovertemplate: "<b>%{{x}}</b> — %{{y}} tracks<extra></extra>",
  marker: {{ color: "#4e9af1" }},
}}], {{
  ...darkLayout,
  margin: {{ t: 10, r: 10, b: 40, l: 40 }},
  bargap: 0.2,
}}, config).then(() => wireClick("chart-year"));

// --- Popularity histogram ---
Plotly.newPlot("chart-popularity", [{{
  type: "bar",
  x: DATA.popularity.x,
  y: DATA.popularity.y,
  hovertemplate: "<b>Score %{{x}}</b> — %{{y}} tracks<extra></extra>",
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
  dragmode: false,
}}, config).then(() => wireClick("chart-popularity"));

// --- Genre bar ---
Plotly.newPlot("chart-genre", [{{
  type: "bar",
  orientation: "h",
  y: DATA.genre.y,
  x: DATA.genre.x,
  hovertemplate: "<b>%{{y}}</b> — %{{x}} tracks<extra></extra>",
  marker: {{ color: "#e07b7b" }},
}}], {{
  ...darkLayout,
  margin: {{ t: 10, r: 20, b: 40, l: 130 }},
  height: 480,
  dragmode: false,
  xaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a", title: {{ text: "Tracks", font: {{ size: 11 }} }} }},
  yaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a", automargin: true }},
}}, config).then(() => wireClick("chart-genre"));

// --- Artist bar ---
Plotly.newPlot("chart-artist", [{{
  type: "bar",
  orientation: "h",
  y: DATA.artist.y,
  x: DATA.artist.x,
  hovertemplate: "<b>%{{y}}</b> — %{{x}} tracks<extra></extra>",
  marker: {{ color: "#54e0a0" }},
}}], {{
  ...darkLayout,
  margin: {{ t: 10, r: 20, b: 40, l: 150 }},
  height: 480,
  dragmode: false,
  xaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a", title: {{ text: "Tracks", font: {{ size: 11 }} }} }},
  yaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a", automargin: true }},
}}, config).then(() => wireClick("chart-artist"));
</script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Saved {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
