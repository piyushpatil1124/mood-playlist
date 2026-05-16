
from flask import Flask, render_template, request
import sys, os, random
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from core import DayArc, MoodVector, PlaylistGenerator

app = Flask(__name__)

BLOCK_COLORS = {
    "morning": ("#fbbf24", "rgba(251,191,36,0.15)"),
    "focus":   ("#60a5fa", "rgba(96,165,250,0.15)"),
    "noon":    ("#34d399", "rgba(52,211,153,0.15)"),
    "slump":   ("#a78bfa", "rgba(167,139,250,0.15)"),
    "burst":   ("#fb7185", "rgba(251,113,133,0.15)"),
    "wind":    ("#818cf8", "rgba(129,140,248,0.15)"),
}

PLAYLIST_NAMES = [
    "Monday Drift", "Tuesday Frequencies", "Wednesday Arc",
    "Thursday Blueprint", "Friday Surge", "Saturday Glow", "Sunday Ease"
]

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Mood Playlist Architect</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#0a0a0f; color:#e8e8f0; font-family:'DM Sans',sans-serif; min-height:100vh; }
    header { padding:32px 24px 0; display:flex; align-items:center; gap:12px; }
    .logo { width:40px; height:40px; border-radius:12px; background:linear-gradient(135deg,#7c3aed,#f472b6); display:flex; align-items:center; justify-content:center; font-size:20px; }
    h1 { font-family:'Playfair Display',serif; font-size:22px; color:#e8e8f0; }
    .sub { font-size:12px; color:#8888a0; letter-spacing:2px; text-transform:uppercase; }
    .container { padding:24px; max-width:900px; margin:0 auto; }
    .controls { background:#1e1e2e; border:1px solid rgba(255,255,255,0.06); border-radius:20px; padding:24px; margin:24px 0; }
    .controls h2 { font-size:14px; color:#8888a0; text-transform:uppercase; letter-spacing:2px; margin-bottom:20px; }
    .sliders { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
    .slider-group label { font-size:13px; color:#8888a0; display:flex; justify-content:space-between; margin-bottom:8px; }
    .slider-group label span { color:#e8e8f0; font-weight:500; }
    input[type=range] { width:100%; appearance:none; height:4px; border-radius:2px; background:#2a2a3e; outline:none; cursor:pointer; }
    input[type=range]::-webkit-slider-thumb { appearance:none; width:16px; height:16px; border-radius:50%; background:#a78bfa; cursor:pointer; }
    .blocks { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin:20px 0; }
    .block-btn { background:#12121a; border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:12px 16px; cursor:pointer; display:flex; align-items:center; gap:10px; transition:all 0.2s; }
    .block-btn.active { background:#1e1e2e; border-color:rgba(167,139,250,0.4); }
    .block-icon { font-size:20px; }
    .block-name { font-size:13px; font-weight:500; }
    .block-time { font-size:11px; color:#8888a0; }
    .gen-btn { width:100%; padding:16px; border-radius:16px; border:none; background:linear-gradient(135deg,#7c3aed,#f472b6); color:white; font-family:'DM Sans',sans-serif; font-size:15px; font-weight:500; cursor:pointer; margin-top:8px; }
    .playlist-title { font-family:'Playfair Display',serif; font-size:24px; font-weight:700; margin:28px 0 4px; }
    .playlist-meta { font-size:13px; color:#8888a0; margin-bottom:16px; }
    .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:24px; }
    .stat { background:#1e1e2e; border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:14px; text-align:center; }
    .stat-val { font-family:'Playfair Display',serif; font-size:22px; font-weight:700; }
    .stat-label { font-size:11px; color:#8888a0; text-transform:uppercase; margin-top:2px; }
    .track { display:flex; align-items:center; gap:12px; padding:10px 14px; border-radius:12px; transition:background 0.2s; }
    .track:hover { background:#1e1e2e; }
    .track-num { font-size:13px; color:#555; width:22px; text-align:center; }
    .track-art { width:42px; height:42px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px; }
    .track-info { flex:1; min-width:0; }
    .track-title { font-size:14px; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .track-artist { font-size:12px; color:#8888a0; margin-top:2px; }
    .track-right { display:flex; align-items:center; gap:10px; flex-shrink:0; }
    .mood-chip { font-size:10px; padding:3px 9px; border-radius:100px; }
    .track-dur { font-size:12px; color:#8888a0; }
    @media(max-width:600px) {
      .sliders { grid-template-columns:1fr; }
      .stats { grid-template-columns:repeat(2,1fr); }
      .blocks { grid-template-columns:1fr; }
      .mood-chip { display:none; }
    }
  </style>
</head>
<body>
<header>
  <div class="logo">🎼</div>
  <div>
    <h1>Playlist Architect</h1>
    <div class="sub">Mood Intelligence</div>
  </div>
</header>
<div class="container">
  <form method="POST" action="/">
    <div class="controls">
      <h2>Tune Your Mood</h2>
      <div class="sliders">
        <div class="slider-group">
          <label>Energy <span id="ev">{{ energy }}</span></label>
          <input type="range" name="energy" min="0" max="100" value="{{ energy }}" oninput="document.getElementById('ev').textContent=this.value">
        </div>
        <div class="slider-group">
          <label>Valence <span id="vv">{{ valence }}</span></label>
          <input type="range" name="valence" min="0" max="100" value="{{ valence }}" oninput="document.getElementById('vv').textContent=this.value">
        </div>
        <div class="slider-group">
          <label>Depth <span id="dv">{{ depth }}</span></label>
          <input type="range" name="depth" min="0" max="100" value="{{ depth }}" oninput="document.getElementById('dv').textContent=this.value">
        </div>
        <div class="slider-group">
          <label>Tempo <span id="tv">{{ tempo }}</span></label>
          <input type="range" name="tempo" min="0" max="100" value="{{ tempo }}" oninput="document.getElementById('tv').textContent=this.value">
        </div>
      </div>
      <h2 style="margin-top:20px">Day Blocks</h2>
      <div class="blocks">
        {% for b in all_blocks %}
        <label class="block-btn {{ 'active' if b.id in selected_blocks else '' }}">
          <input type="checkbox" name="blocks" value="{{ b.id }}" {{ 'checked' if b.id in selected_blocks else '' }} style="display:none" onchange="this.closest('.block-btn').classList.toggle('active',this.checked)">
          <div class="block-icon">{{ b.icon }}</div>
          <div>
            <div class="block-name">{{ b.name }}</div>
            <div class="block-time">{{ b.time_range }}</div>
          </div>
        </label>
        {% endfor %}
      </div>
      <button type="submit" class="gen-btn">✦ Architect My Playlist</button>
    </div>
  </form>
  {% if playlist %}
  <div class="playlist-title">{{ playlist_name }}</div>
  <div class="playlist-meta">{{ playlist|length }} tracks · {{ duration }} · {{ mood_label }} arc</div>
  <div class="stats">
    <div class="stat"><div class="stat-val">{{ playlist|length }}</div><div class="stat-label">Tracks</div></div>
    <div class="stat"><div class="stat-val">{{ duration }}</div><div class="stat-label">Duration</div></div>
    <div class="stat"><div class="stat-val">{{ avg_energy }}</div><div class="stat-label">Avg Energy</div></div>
    <div class="stat"><div class="stat-val">{{ genre_count }}</div><div class="stat-label">Genres</div></div>
  </div>
  {% for i, track, block, chip_color, chip_bg in playlist %}
  <div class="track">
    <div class="track-num">{{ i }}</div>
    <div class="track-art" style="background:{{ chip_bg }}">{{ track.icon }}</div>
    <div class="track-info">
      <div class="track-title">{{ track.title }}</div>
      <div class="track-artist">{{ track.artist }}</div>
    </div>
    <div class="track-right">
      <span class="mood-chip" style="background:{{ chip_bg }};color:{{ chip_color }}">{{ track.mood_vec.to_label() }}</span>
      <span class="track-dur">{{ track.duration_str }}</span>
    </div>
  </div>
  {% endfor %}
  {% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    energy  = int(request.form.get("energy",  70))
    valence = int(request.form.get("valence", 65))
    depth   = int(request.form.get("depth",   50))
    tempo   = int(request.form.get("tempo",   75))
    arc = DayArc()
    all_blocks = arc.DEFAULT_BLOCKS
    selected_blocks = request.form.getlist("blocks")
    if not selected_blocks:
        selected_blocks = [b.id for b in all_blocks]
    arc.enable(*selected_blocks)
    arc.global_mood = MoodVector(energy, valence, depth, tempo)
    playlist_data = None
    duration = ""
    mood_label = ""
    avg_energy = 0
    genre_count = 0
    playlist_name = ""
    if request.method == "POST":
        gen = PlaylistGenerator()
        raw = gen.generate(arc, tracks_per_block=4)
        playlist_data = []
        for i, (track, block) in enumerate(raw, 1):
            color, bg = BLOCK_COLORS.get(block.id, ("#a78bfa", "rgba(167,139,250,0.15)"))
            playlist_data.append((i, track, block, color, bg))
        duration = gen.total_duration(raw)
        mood_label = arc.dominant_mood().to_label()
        avg_energy = round(sum(t.mood_vec.energy for t, _ in raw) / len(raw))
        genre_count = len({t.genre for t, _ in raw})
        playlist_name = PLAYLIST_NAMES[datetime.now().weekday()]
    return render_template_string(HTML,
        energy=energy, valence=valence, depth=depth, tempo=tempo,
        all_blocks=all_blocks, selected_blocks=selected_blocks,
        playlist=playlist_data, duration=duration,
        mood_label=mood_label, avg_energy=avg_energy,
        genre_count=genre_count, playlist_name=playlist_name,
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
