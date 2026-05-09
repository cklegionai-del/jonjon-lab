import os
import subprocess
import requests
from datetime import datetime
import chromadb
from ollama import embeddings, chat
import time
import random

OUTPUT_DIR = os.path.expanduser("~/Desktop/HTML_Outputs")
SEARXNG = "http://localhost:8888"
COLLECTION = "html_templates"

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection(COLLECTION)

def search_web(niche):
    print(f"🌐 أبحث عن أحسن مواقع {niche}...")
    queries = [
        f"best {niche} website design 2025",
        f"{niche} landing page inspiration premium",
        f"award winning {niche} website UI"
    ]
    results = []
    for q in queries:
        try:
            r = requests.get(f"{SEARXNG}/search", params={
                "q": q, "format": "json", "categories": "general"
            }, timeout=10)
            data = r.json()
            for item in data.get("results", [])[:3]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")
                })
        except Exception as e:
            print(f"  ⚠️ {e}")
    print(f"  ✅ {len(results)} نتيجة")
    return results

def analyze_research(niche, results):
    print("\n🧠 qwen2.5:32b يحلل الأبحاث...")
    context = "\n".join([
        f"- {r['title']}: {r['content'][:200]}"
        for r in results[:10]
    ])
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            r = chat(
                model="qwen2.5:32b",
                messages=[{
                    "role": "system",
                    "content": "You are a UI/UX research analyst. Analyze web search results and extract design patterns."
                }, {
                    "role": "user",
                    "content": f"""Niche: {niche}

Search results about top {niche} websites:
{context}

Extract:
1. Color palettes used by top sites
2. Key sections every premium {niche} site has
3. Typography trends
4. Animation/interaction patterns
5. What makes them premium and trustworthy

Be specific and actionable for an HTML developer."""
                }],
                options={"temperature": 0.3}
            )
            analysis = r['message']['content']
            print(f"📊 Analysis ready")
            return analysis
        except Exception as e:
            print(f"  ⚠️ Error in analysis (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"  ⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def search_templates(prompt):
    print("\n📚 أبحث في قوالبك المحلية...")
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            resp = embeddings(model="bge-m3", prompt=prompt)
            results = collection.query(
                query_embeddings=[resp['embedding']],
                n_results=2,
                where={"type": "html"}
            )
            templates = []
            for meta in results['metadatas'][0]:
                try:
                    with open(meta['path'], 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    templates.append({
                        "template": meta['template'],
                        "content": content[:4000]
                    })
                    print(f"  ✅ {meta['template']}")
                except:
                    pass
            return templates
        except Exception as e:
            print(f"  ⚠️ Error in template search (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"  ⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def generate(niche, prompt, analysis, templates):
    print("\n✍️  qwen3-coder يبني...")
    template_ctx = "\n\n".join([
        f"=== {t['template']} ===\n{t['content']}"
        for t in templates
    ])
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            r = chat(
                model="qwen3-coder:30b",
                messages=[{
                    "role": "system",
                    "content": """Expert HTML/CSS/JS developer building premium websites.
Return ONLY complete HTML starting with <!DOCTYPE html>.
No markdown. No explanations. Pure production-ready code.
Use: Google Fonts, Tailwind CDN, smooth animations, modern effects."""
                }, {
                    "role": "user",
                    "content": f"""Build a premium {niche} website.

RESEARCH INSIGHTS (from top {niche} sites):
{analysis}

USER REQUEST: {prompt}

REFERENCE TEMPLATES (use their structure/patterns):
{template_ctx}

Build something that competes with the best {niche} sites in the world."""
                }],
                options={"temperature": 0.6}
            )
            return r['message']['content']
        except Exception as e:
            print(f"  ⚠️ Error in generation (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"  ⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def review_and_improve(html, niche, prompt):
    print("\n👁️  reviewer يراجع...")
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            feedback = chat(
                model="qwen3:8b",
                messages=[{
                    "role": "system",
                    "content": f"Senior frontend reviewer specializing in {niche} websites. Give 3 brutal specific improvements."
                }, {
                    "role": "user",
                    "content": f"Request: {prompt}\nHTML:\n{html[:3000]}"
                }],
                options={"temperature": 0.2}
            )['message']['content']
            
            print(f"📋 Feedback:\n{feedback}\n")
            print("✨ يحسن...")
            
            improved = chat(
                model="qwen3:8b",
                messages=[{
                    "role": "system",
                    "content": "Expert HTML developer. Apply ALL feedback. Return ONLY complete HTML starting with <!DOCTYPE html>."
                }, {
                    "role": "user",
                    "content": f"Original: {prompt}\nHTML:\n{html}\nFix:\n{feedback}"
                }],
                options={"temperature": 0.4}
            )['message']['content']
            return improved
        except Exception as e:
            print(f"  ⚠️ Error in review and improvement (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"  ⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def clean(html):
    for marker in ["```html", "```"]:
        if marker in html:
            parts = html.split(marker)
            html = parts[1].split("```")[0] if len(parts) > 1 else html
            break
    return html.strip()

def save_and_open(html, name):
    timestamp = datetime.now().strftime("%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{name}_{timestamp}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    subprocess.run(["open", filepath])
    return filepath

def main():
    print("🚀 jonjon Research Agent — Web Research + RAG + Coder + Reviewer")
    print("=" * 60)
    niche = input("🎯 شنو الـ niche؟ (مثال: luxury real estate, coffee shop, saas): ")
    prompt = input("📝 تفاصيل إضافية (أو Enter للمتابعة): ") or f"premium {niche} website"
    name = input("💾 اسم الملف: ") or niche.replace(" ", "_")

    try:
        web_results = search_web(niche)
        analysis = analyze_research(niche, web_results)
        templates = search_templates(niche)
        
        html = clean(generate(niche, prompt, analysis, templates))
        html = clean(review_and_improve(html, niche, prompt))
        
        path = save_and_open(html, name)
        print(f"\n🎉 جاهز! → {path}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check if Ollama is running and all services are accessible.")

if __name__ == "__main__":
    main()
