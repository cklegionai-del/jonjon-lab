import ollama
import os
import subprocess
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/Desktop/HTML_Outputs")
ROUNDS = 3

def generate(prompt):
    print("🧠 [1/1] qwen3-coder يكتب النسخة الأولى...")
    r = ollama.chat(
        model="qwen3-coder:30b",
        messages=[{
            "role": "system",
            "content": "You are an expert HTML/CSS/JS developer. Generate ONLY complete beautiful HTML. No explanations. No markdown. Just pure HTML starting with <!DOCTYPE html>. Use Tailwind CDN, Google Fonts, smooth animations, glassmorphism or modern effects."
        }, {"role": "user", "content": prompt}],
        options={"temperature": 0.7}
    )
    return r['message']['content']

def review(html, prompt, round_num):
    print(f"👁️  [round {round_num}] qwen3:8b يراجع...")
    r = ollama.chat(
        model="qwen3:8b",
        messages=[{
            "role": "system",
            "content": """You are a brutal senior frontend reviewer. 
Give exactly 3 specific technical improvements. Be direct and precise.
Focus on: visual impact, animations, UX, missing sections, mobile responsiveness."""
        }, {
            "role": "user",
            "content": f"Request: {prompt}\n\nHTML (first 4000 chars):\n{html[:4000]}"
        }],
        options={"temperature": 0.2}
    )
    return r['message']['content']

def improve(html, feedback, prompt, round_num):
    print(f"✨ [round {round_num}] qwen3-coder يحسن...")
    r = ollama.chat(
        model="qwen3-coder:30b",
        messages=[{
            "role": "system",
            "content": "You are an expert HTML developer. Apply ALL feedback and return ONLY improved complete HTML starting with <!DOCTYPE html>. No markdown. No explanations."
        }, {
            "role": "user",
            "content": f"Original request: {prompt}\n\nCurrent HTML:\n{html}\n\nMust fix:\n{feedback}\n\nReturn complete improved HTML:"
        }],
        options={"temperature": 0.4}
    )
    return r['message']['content']

def clean(html):
    if "```html" in html:
        html = html.split("```html")[1].split("```")[0]
    elif "```" in html:
        html = html.split("```")[1].split("```")[0]
    return html.strip()

def save(html, name, version):
    timestamp = datetime.now().strftime("%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{name}_v{version}_{timestamp}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return filepath

def main():
    print("🚀 jonjon HTML Agent v3 — Multi-Round Refinement")
    print("=" * 50)
    prompt = input("📝 شنو تحب تعمل؟ : ")
    name = input("💾 اسم الملف: ") or "page"
    
    html = clean(generate(prompt))
    save(html, name, 0)
    print("💾 نسخة أولى محفوظة\n")

    for i in range(1, ROUNDS + 1):
        print(f"\n{'='*50}")
        print(f"🔄 Round {i}/{ROUNDS}")
        print('='*50)
        
        feedback = review(html, prompt, i)
        print(f"\n📋 Feedback:\n{feedback}\n")
        
        html = clean(improve(html, feedback, prompt, i))
        path = save(html, name, i)
        print(f"💾 نسخة {i} محفوظة")

    subprocess.run(["open", path])
    print(f"\n🎉 النسخة النهائية بعد {ROUNDS} rounds → {path}")

if __name__ == "__main__":
    main()
