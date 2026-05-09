import os
import subprocess
from datetime import datetime
import chromadb
from ollama import embeddings, chat

OUTPUT_DIR = os.path.expanduser("~/Desktop/HTML_Outputs")
COLLECTION = "html_templates"

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection(COLLECTION)

def search_templates(prompt, n=2):
    print("🔍 أبحث في القوالب...")
    resp = embeddings(model="bge-m3", prompt=prompt)
    results = collection.query(
        query_embeddings=[resp['embedding']],
        n_results=n,
        where={"type": "html"}
    )
    templates = []
    for i, path in enumerate(results['metadatas'][0]):
        with open(path['path'], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        templates.append({
            "template": path['template'],
            "file": path['file'],
            "content": content[:5000]
        })
        print(f"  ✅ {path['template']}/{path['file']}")
    return templates

def generate(prompt, templates):
    print("\n🧠 qwen3-coder يكتب بناءً على القوالب...")
    template_context = "\n\n".join([
        f"=== Template: {t['template']} ===\n{t['content']}"
        for t in templates
    ])
    r = chat(
        model="qwen3-coder:30b",
        messages=[{
            "role": "system",
            "content": """You are an expert HTML developer. 
You have reference templates to inspire from.
Generate a COMPLETE, STUNNING, PRODUCTION-READY HTML file.
- Use the best patterns from the reference templates
- Add smooth animations and modern effects
- Make it fully responsive
- Return ONLY pure HTML starting with <!DOCTYPE html>
- No markdown, no explanations"""
        }, {
            "role": "user",
            "content": f"REQUEST: {prompt}\n\nREFERENCE TEMPLATES:\n{template_context}"
        }],
        options={"temperature": 0.6}
    )
    return r['message']['content']

def review_and_improve(html, prompt):
    print("\n👁️  qwen3:8b يراجع...")
    feedback = chat(
        model="qwen3:8b",
        messages=[{
            "role": "system",
            "content": "Senior frontend reviewer. Give 3 specific improvements. Be technical and direct."
        }, {
            "role": "user",
            "content": f"Request: {prompt}\n\nHTML:\n{html[:3000]}"
        }],
        options={"temperature": 0.2}
    )['message']['content']
    
    print(f"📋 Feedback:\n{feedback}\n")
    print("✨ qwen3-coder يحسن...")
    
    improved = chat(
        model="qwen3-coder:30b",
        messages=[{
            "role": "system",
            "content": "Expert HTML developer. Apply ALL feedback. Return ONLY complete HTML starting with <!DOCTYPE html>. No markdown."
        }, {
            "role": "user",
            "content": f"Request: {prompt}\n\nHTML:\n{html}\n\nFix:\n{feedback}"
        }],
        options={"temperature": 0.4}
    )['message']['content']
    return improved

def clean(html):
    if "```html" in html:
        html = html.split("```html")[1].split("```")[0]
    elif "```" in html:
        html = html.split("```")[1].split("```")[0]
    return html.strip()

def save_and_open(html, name):
    timestamp = datetime.now().strftime("%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{name}_{timestamp}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    subprocess.run(["open", filepath])
    return filepath

def main():
    print("🚀 jonjon HTML Agent — RAG + Coder + Reviewer")
    print("=" * 50)
    prompt = input("📝 شنو تحب تعمل؟ : ")
    name = input("💾 اسم الملف: ") or "page"

    templates = search_templates(prompt)
    html = clean(generate(prompt, templates))
    html = clean(review_and_improve(html, prompt))
    path = save_and_open(html, name)
    
    print(f"\n🎉 جاهز! → {path}")

if __name__ == "__main__":
    main()
