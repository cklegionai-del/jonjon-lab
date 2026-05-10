import ollama
import os
import subprocess
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/Desktop/HTML_Outputs")

def generate(prompt, system_prompt):
    print("\n🧠 qwen3-coder يكتب...")
    r = ollama.chat(
        model="qwen3-coder:30b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0.7}
    )
    return r['message']['content']

def clean(html):
    if "```html" in html:
        html = html.split("```html")[1].split("```")[0]
    elif "```" in html:
        html = html.split("```")[1].split("```")[0]
    return html.strip()

def save_and_open(html, name, version=1):
    timestamp = datetime.now().strftime("%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{name}_v{version}_{timestamp}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    subprocess.run(["open", filepath])
    return filepath

def ask_refinements():
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 شنو تحب تبدل؟ (اختار عدة خيارات مفصولة بفاصلة، مثال: 1,3)

[1] الألوان والـ theme
[2] أضف/احذف sections
[3] المحتوى والنصوص
[4] Animations وتأثيرات
[5] Layout وترتيب
[6] اكتب تعديل حر
[0] حفظ وخروج
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    choices = input("اختارك: ").strip()
    
    if choices == "0":
        return None
    
    refinements = []
    
    for c in choices.split(","):
        c = c.strip()
        if c == "1":
            colors = input("  🎨 شنو الألوان تحبها؟ (مثال: dark black with gold, navy blue with silver): ")
            refinements.append(f"Change color scheme to: {colors}")
        elif c == "2":
            sections = input("  📦 شنو الـ sections تحب تضيف أو تحذف؟: ")
            refinements.append(f"Sections changes: {sections}")
        elif c == "3":
            content = input("  ✍️  شنو التغييرات في المحتوى؟: ")
            refinements.append(f"Content changes: {content}")
        elif c == "4":
            animations = input("  ✨ شنو الـ animations تحبها؟ (مثال: smooth scroll, parallax, fade in): ")
            refinements.append(f"Add animations: {animations}")
        elif c == "5":
            layout = input("  📐 شنو تغييرات الـ layout؟: ")
            refinements.append(f"Layout changes: {layout}")
        elif c == "6":
            free = input("  💬 اكتب تعديلك هنا: ")
            refinements.append(free)
    
    return refinements

def refine(html, refinements, original_prompt):
    print("\n✨ يطبق التعديلات...")
    changes = "\n".join([f"- {r}" for r in refinements])
    
    r = ollama.chat(
        model="qwen3-coder:30b",
        messages=[{
            "role": "system",
            "content": "Expert HTML developer. Apply ALL requested changes precisely. Return ONLY complete HTML starting with <!DOCTYPE html>. No markdown."
        }, {
            "role": "user",
            "content": f"""Original request: {original_prompt}

Current HTML:
{html}

Apply these changes:
{changes}

Return the complete improved HTML:"""
        }],
        options={"temperature": 0.5}
    )
    return r['message']['content']

def main():
    SYSTEM_PROMPT = """You are an expert HTML/CSS/JS developer specializing in premium, luxury websites.
Generate ONLY complete, stunning HTML files starting with <!DOCTYPE html>.
No explanations. No markdown. Pure production-ready HTML.
Use: Google Fonts, Tailwind CDN, smooth animations, glassmorphism, modern effects.
Make it visually stunning and premium."""

    print("🚀 jonjon HTML Agent v4 — Interactive Refinement")
    print("=" * 50)
    
    prompt = input("📝 شنو تحب تعمل؟ : ")
    name = input("💾 اسم الملف: ") or "page"
    
    html = clean(generate(prompt, SYSTEM_PROMPT))
    version = 1
    path = save_and_open(html, name, version)
    print(f"\n✅ النسخة {version} جاهزة → {path}")
    
    while True:
        refinements = ask_refinements()
        
        if refinements is None:
            print(f"\n🎉 النسخة النهائية محفوظة → {path}")
            break
        
        html = clean(refine(html, refinements, prompt))
        version += 1
        path = save_and_open(html, name, version)
        print(f"\n✅ النسخة {version} جاهزة → {path}")

if __name__ == "__main__":
    main()
