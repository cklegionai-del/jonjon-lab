import ollama
import os
import subprocess
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/Desktop/HTML_Outputs")

def generate(prompt):
    print("🧠 qwen3-coder يكتب...")
    r = ollama.chat(
        model="qwen3-coder:30b",
        messages=[{
            "role": "system",
            "content": "You are an expert HTML/CSS/JS developer. Generate ONLY complete beautiful HTML. No explanations. No markdown. Just pure HTML starting with <!DOCTYPE html>. Use Tailwind CDN, modern fonts, animations."
        }, {
            "role": "user",
            "content": prompt
        }],
        options={"temperature": 0.7}
    )
    return r['message']['content']

def review(html, original_prompt):
    print("👁️  qwen3:8b يراجع...")
    r = ollama.chat(
        model="qwen3:8b",
        messages=[{
            "role": "system",
            "content": "You are a senior frontend reviewer. Review HTML code and give 3 specific improvements needed. Be concise and technical."
        }, {
            "role": "user",
            "content": f"Original request: {original_prompt}\n\nHTML to review:\n{html[:3000]}"
        }],
        options={"temperature": 0.3}
    )
    return r['message']['content']

def improve(html, feedback, original_prompt):
    print("✨ qwen3-coder يحسن...")
    r = ollama.chat(
        model="qwen3-coder:30b",
        messages=[{
            "role": "system",
            "content": "You are an expert HTML developer. Improve the HTML based on feedback. Return ONLY complete HTML starting with <!DOCTYPE html>. No markdown."
        }, {
            "role": "user",
            "content": f"Original request: {original_prompt}\n\nCurrent HTML:\n{html}\n\nReviewer feedback:\n{feedback}\n\nReturn improved HTML:"
        }],
        options={"temperature": 0.5}
    )
    return r['message']['content']

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
    print("🚀 jonjon HTML Agent v2 — Coder + Reviewer")
    print("=" * 45)
    prompt = input("📝 شنو تحب تعمل؟ : ")
    name = input("💾 اسم الملف: ") or "page"

    # Round 1
    html = clean(generate(prompt))
    
    # Review
    feedback = review(html, prompt)
    print(f"\n📋 الـ Reviewer قال:\n{feedback}\n")
    
    # Improve
    final_html = clean(improve(html, feedback, prompt))
    
    path = save_and_open(final_html, name)
    print(f"\n🎉 جاهز بعد review! → {path}")

if __name__ == "__main__":
    main()
