import sys
import requests

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"  # سريع وممتاز في الترجمة

# ========== دالة الترجمة ==========
def translate(text, direction="auto"):
    """
    direction: 
        "auto" - يكتشف اللغة ويترجم للعكس
        "to_en" - يترجم من العربية إلى الإنجليزية
        "to_ar" - يترجم من الإنجليزية إلى العربية
    """
    
    if direction == "auto":
        # اكتشاف اللغة بسيط: إذا كان فيه حروف عربية = عربي
        if any('\u0600' <= c <= '\u06ff' for c in text):
            direction = "to_en"
        else:
            direction = "to_ar"
    
    if direction == "to_en":
        prompt = f"""Translate the following Arabic text into English. 
Keep the meaning exact. Return ONLY the translation, nothing else.

Arabic: {text}

English:"""
    else:
        prompt = f"""Translate the following English text into Arabic.
Keep the meaning exact. Use proper Modern Standard Arabic. Return ONLY the translation, nothing else.

English: {text}

Arabic:"""
    
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })
    
    if response.status_code == 200:
        return response.json().get("response", "").strip()
    return f"خطأ: {response.status_code}"

# ========== واجهة سطر الأوامر ==========
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("📋 الاستخدام:")
        print("  python agent.py to_en 'النص العربي'")
        print("  python agent.py to_ar 'English text'")
        print("  python agent.py auto 'نص'  ← يكتشف اللغة تلقائياً")
    else:
        command = sys.argv[1]
        text = " ".join(sys.argv[2:])
        
        result = translate(text, command)
        print(f"\n📝 الترجمة:\n{result}\n")
