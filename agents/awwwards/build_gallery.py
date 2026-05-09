import json
import os
import base64

LIBRARY_DIR = os.path.expanduser("~/jonjon-lab/agents/awwwards/library")
OUTPUT = os.path.expanduser("~/Desktop/awwwards_library.html")

CATEGORIES = {
    "real-estate-architecture": {"label": "Real Estate & Architecture", "emoji": "🏛️"},
    "restaurant-hotel": {"label": "Restaurant & Hotel", "emoji": "🍽️"},
    "fashion-luxury": {"label": "Fashion & Luxury", "emoji": "💎"},
    "portfolio-agency": {"label": "Portfolio & Agency", "emoji": "🎨"},
    "ecommerce": {"label": "E-commerce", "emoji": "🛍️"},
    "saas-tech": {"label": "SaaS & Tech", "emoji": "🚀"},
}

def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    except:
        return ""

master_path = os.path.join(LIBRARY_DIR, "master.json")
with open(master_path) as f:
    all_sites = json.load(f)

cards_html = ""
for cat_id, cat_info in CATEGORIES.items():
    sites = all_sites.get(cat_id, [])
    if not sites:
        continue
    
    cards_html += f"""
    <div class="category" id="{cat_id}">
      <div class="cat-header">
        <span class="cat-emoji">{cat_info['emoji']}</span>
        <h2>{cat_info['label']}</h2>
        <span class="cat-count">{len(sites)} sites</span>
      </div>
      <div class="grid">
    """
    
    for site in sites:
        img = img_to_base64(site.get("screenshot", ""))
        img_tag = f'<img src="{img}" alt="{site["name"]}">' if img else '<div class="no-img">No Preview</div>'
        url = site.get("awwwards_url", "#")
        cards_html += f"""
        <a class="card" href="{url}" target="_blank">
          <div class="card-img">{img_tag}</div>
          <div class="card-info">
            <div class="card-name">{site['name']}</div>
            <div class="card-rank">#{site['rank']}</div>
          </div>
        </a>
        """
    
    cards_html += "</div></div>"

nav_html = "".join([
    f'<a href="#{cid}" class="nav-item">{ci["emoji"]} {ci["label"]}</a>'
    for cid, ci in CATEGORIES.items()
])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>jonjon-lab // Awwwards Library</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;600&display=swap');
  *{{margin:0;padding:0;box-sizing:border-box}}
  :root{{--bg:#080810;--surface:#0f0f1a;--border:#1a1a2e;--accent:#7c3aed;--text:#e2e8f0;--muted:#475569}}
  body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh}}
  header{{padding:2rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:1rem}}
  .logo{{font-family:'IBM Plex Mono',monospace;font-size:1.2rem;color:var(--accent)}}
  .subtitle{{color:var(--muted);font-size:0.85rem}}
  nav{{position:sticky;top:0;z-index:100;background:var(--surface);border-bottom:1px solid var(--border);padding:0.75rem 2rem;display:flex;gap:0.5rem;overflow-x:auto}}
  .nav-item{{font-size:0.75rem;padding:0.4rem 0.8rem;border-radius:6px;border:1px solid var(--border);color:var(--muted);text-decoration:none;white-space:nowrap;transition:all 0.2s}}
  .nav-item:hover{{border-color:var(--accent);color:var(--text)}}
  .category{{padding:2rem;border-bottom:1px solid var(--border)}}
  .cat-header{{display:flex;align-items:center;gap:0.75rem;margin-bottom:1.5rem}}
  .cat-emoji{{font-size:1.5rem}}
  .cat-header h2{{font-size:1.1rem;font-weight:600}}
  .cat-count{{font-size:0.7rem;background:rgba(124,58,237,0.15);color:var(--accent);padding:0.2rem 0.6rem;border-radius:4px;border:1px solid rgba(124,58,237,0.3)}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem}}
  .card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;text-decoration:none;color:inherit;transition:all 0.2s;display:block}}
  .card:hover{{border-color:var(--accent);transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.4)}}
  .card-img{{height:140px;overflow:hidden;background:#0a0a14}}
  .card-img img{{width:100%;height:100%;object-fit:cover}}
  .no-img{{height:100%;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:0.75rem}}
  .card-info{{padding:0.75rem;display:flex;justify-content:space-between;align-items:center}}
  .card-name{{font-size:0.8rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:160px}}
  .card-rank{{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:var(--accent)}}
  footer{{text-align:center;padding:2rem;color:var(--muted);font-size:0.75rem;font-family:'IBM Plex Mono',monospace}}
</style>
</head>
<body>
<header>
  <div>
    <div class="logo">jonjon-lab // awwwards library</div>
    <div class="subtitle">60 sites · 6 categories · scraped from awwwards.com</div>
  </div>
</header>
<nav>{nav_html}</nav>
{cards_html}
<footer>jonjon-lab · hichem · {__import__('datetime').datetime.now().year}</footer>
</body>
</html>"""

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Gallery: {OUTPUT}")
