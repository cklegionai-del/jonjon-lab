import json
import os
import sys
import requests
from datetime import datetime

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def ask_model(model, prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    if response.status_code == 200:
        return response.json().get("response", "")
    return ""

def translate_to_prompt(description_ar):
    """يترجم الوصف العربي إلى Prompt إنجليزي احترافي"""
    prompt = f"""You are a professional AI image prompt engineer.
Translate this Arabic description into a detailed, professional English prompt
for Flux.1 image generation. Add style, lighting, camera angle, and mood details.
Return ONLY the prompt, no explanation.

Arabic: {description_ar}

Professional Prompt:"""
    
    return ask_model("gpt-oss:20b", prompt)

def generate_image_ideas(topic_ar, count=5):
    """يولد أفكاراً لصور بناءً على موضوع"""
    prompt = f"""You are a creative director. Given this Arabic topic:
"{topic_ar}"

Generate {count} creative image ideas. For each:
1. Title (in English)
2. Scene description (in English, detailed)
3. Best style (anime, realistic, cinematic, oil painting, etc.)

Format:
IDEA 1:
Title: [title]
Scene: [description]
Style: [style]

..."""
    
    return ask_model("gpt-oss:20b", prompt)

def build_character(description_ar):
    """يبني 'الكتاب المقدس' لشخصية"""
    prompt = f"""You are a character designer. Based on this Arabic description:
"{description_ar}"

Create a detailed character bible:
1. Name
2. Age
3. Physical appearance (face, hair, eyes, height, build)
4. Clothing style
5. Distinctive marks (scars, tattoos, accessories)
6. Personality traits
7. Background story (2 sentences)

Write in English. Keep it consistent for image generation."""
    
    return ask_model("gpt-oss:20b", prompt)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("📋 الأوامر:")
        print('  python agent.py prompt "وصف الصورة بالعربية"')
        print('  python agent.py ideas "موضوع" [عدد]')
        print('  python agent.py character "وصف الشخصية بالعربية"')
    else:
        command = sys.argv[1]
        text = " ".join(sys.argv[2:])
        
        if command == "prompt":
            print("🎨 جاري تحويل الوصف إلى Prompt احترافي...")
            result = translate_to_prompt(text)
            print(f"\n📝 الـ Prompt:\n{result}")
        
        elif command == "ideas":
            count = 5
            parts = text.split()
            if parts and parts[-1].isdigit():
                count = int(parts[-1])
                text = " ".join(parts[:-1])
            print(f"💡 جاري توليد {count} أفكار...")
            result = generate_image_ideas(text, count)
            print(result)
        
        elif command == "character":
            print("👤 جاري بناء شخصية...")
            result = build_character(text)
            print(result)
