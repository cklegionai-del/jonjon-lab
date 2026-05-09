import ollama
import os
import subprocess
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/Desktop/HTML_Outputs")

def generate_html(prompt: str) -> str:
    print(f"🧠 qwen3-coder يشتغل...")
    
    response = ollama.chat(
        model="qwen3-coder:30b",
        messages=[{
            "role": "system",
            "content": """You are an expert HTML/CSS/JS developer. 
Generate ONLY complete, beautiful, modern HTML files.
No explanations. No markdown. Just pure HTML code starting with <!DOCTYPE html>.
Use Tailwind CDN, modern fonts, animations. Make it visually stunning."""
        }, {
            "role": "user", 
            "content": prompt
        }],
        options={"temperature": 0.7}
    )
    
    return response['message']['content']

def save_and_open(html: str, name: str) -> str:
    # نظف الكود
    if "```html" in html:
        html = html.split("```html")[1].split("```")[0]
    elif "```" in html:
        html = html.split("```")[1].split("```")[0]
    
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{name}_{timestamp}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ محفوظ: {filepath}")
    subprocess.run(["open", filepath])
    return filepath

def main():
    print("🚀 jonjon HTML Agent")
    print("=" * 40)
    prompt = input("📝 شنو تحب تعمل؟ : ")
    name = input("💾 اسم الملف (بدون .html): ") or "page"
    
    html = generate_html(prompt)
    path = save_and_open(html, name)
    print(f"\n🎉 جاهز! → {path}")

if __name__ == "__main__":
    main()
