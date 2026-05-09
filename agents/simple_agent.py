#!/usr/bin/env python3
"""
jonjon Simple Agent v1.0
يبني HTML بسيط من niche
"""

import ollama

def build_html(niche: str) -> str:
    """يبني HTML بسيط"""
    
    print(f"🚀 Building landing page for: {niche}")
    
    response = ollama.chat(
        model="qwen3:8b",  # سريع للتجربة
        messages=[
            {
                "role": "system",
                "content": "You are an expert HTML developer. Return ONLY complete HTML code."
            },
            {
                "role": "user",
                "content": f"Create a beautiful landing page for: {niche}"
            }
        ],
        options={
            "temperature": 0.7,
            "num_ctx": 4096,
            "num_predict": 2000
        }
    )
    
    html = response['message']['content']
    
    # تنظيف: شيل ```html و ```
    html = html.replace("```html", "").replace("```", "").strip()
    
    return html

def save_html(html: str, filename: str = "output"):
    """يحفظ HTML"""
    filepath = f"/Users/hichem/jonjon-lab/output/{filename}.html"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Saved: {filepath}")
    return filepath

# === MAIN ===
if __name__ == "__main__":
    niche = input("🎯 Niche? (e.g., coffee shop): ") or "coffee shop"
    
    html = build_html(niche)
    save_html(html, niche.replace(" ", "_"))
    
    print(f"\n🎉 Done! Open: file:///Users/hichem/jonjon-lab/output/{niche.replace(' ', '_')}.html")#!/usr/bin/env python3
import ollama

def build_html(niche: str) -> str:
    print(f"🚀 Building for: {niche}")
    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": "You are an expert HTML developer. Return ONLY complete HTML code."},
            {"role": "user", "content": f"Create a beautiful landing page for: {niche}"}
        ],
        options={"temperature": 0.7, "num_ctx": 4096, "num_predict": 2000}
    )
    html = response['message']['content']
    html = html.replace("```html", "").replace("```", "").strip()
    return html

def save_html(html: str, filename: str = "output"):
    filepath = f"/Users/hichem/jonjon-lab/output/{filename}.html"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Saved: {filepath}")
    return filepath

if __name__ == "__main__":
    niche = input("🎯 Niche? ") or "coffee shop"
    html = build_html(niche)
    save_html(html, niche.replace(" ", "_"))
    print(f"\n🎉 Open: file:///Users/hichem/jonjon-lab/output/{niche.replace(' ', '_')}.html")
