import json
import os
import sys
import requests
from datetime import datetime
from urllib.parse import quote

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
SEARXNG_URL = "http://localhost:8080/search?format=json&q="
MEMORY_AGENT = os.path.join(os.path.dirname(__file__), "..", "alhafez", "agent.py")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

os.makedirs(DATA_DIR, exist_ok=True)

# ========== استدعاء نموذج ==========
def ask_model(model, prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    if response.status_code == 200:
        return response.json().get("response", "")
    return ""

# ========== البحث في الويب ==========
def search_web(query, num_results=5):
    """يبحث في الويب باستخدام SearXNG الحقيقي"""
    try:
        url = SEARXNG_URL + quote(query)
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])[:num_results]
            if results:
                return results
    except:
        pass
    return []

def simulate_search(query):
    """محاكاة البحث عند عدم توفر SearXNG"""
    prompt = f"""أنت محرك بحث. أجب عن هذا الاستفسار كأنك بحثت في الويب.
    قدم 3 نتائج. لكل نتيجة: عنوان، رابط وهمي، ووصف من سطرين.
    الاستفسار: {query}
    """
    result = ask_model("gpt-oss:20b", prompt)
    return [{"title": "نتيجة محاكاة", "url": "محاكاة", "content": result}]

# ========== تصنيف النتائج ==========
def classify_results(results, query):
    """يصنف النتائج حسب الأهمية"""
    text_results = "\n".join([f"- {r.get('title', '')}: {r.get('content', '')[:200]}" for r in results])
    
    prompt = f"""صنف هذه النتائج إلى 3 فئات:
    🔴 مهم جداً: نتيجة فريدة ومفيدة
    🟡 مفيد: نتيجة جيدة لكنها متوقعة
    ⚪ عادي: نتيجة عامة

    الاستفسار: {query}
    النتائج:
    {text_results}
    
    أعد التصنيف فقط.
    """
    return ask_model("gpt-oss:20b", prompt)

# ========== حفظ النتائج ==========
def save_results(query, results, classification):
    """يحفظ النتائج في مجلد data ويرسلها للحافظ"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"search_{timestamp}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    data = {
        "query": query,
        "timestamp": timestamp,
        "classification": classification,
        "results": [{"title": r.get("title"), "url": r.get("url"), "content": r.get("content", "")[:500]} for r in results]
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    save_to_memory = f"python3 {MEMORY_AGENT} save 'بحث عن: {query}. {len(results)} نتيجة. المحفوظ: {filename}' searches بحث,راصد"
    os.system(save_to_memory)
    
    return filepath

# ========== البحث الكامل مع التقرير ==========
def deep_search(query, save=True):
    """يبحث ويصنف ويحفظ ويعيد تقريراً كاملاً"""
    print(f"🔍 جاري البحث عن: {query}")
    
    # 1. البحث
    results = search_web(query)
    
    # إذا فشل البحث الحي، نستخدم المحاكاة
    if not results:
        print("⚠️ لم تعثر SearXNG على نتائج. جاري المحاكاة...")
        results = simulate_search(query)
    
    if not results:
        return "❌ لم أجد نتائج."
    
    print(f"📊 وجدت {len(results)} نتيجة. جاري التصنيف...")
    
    # 2. التصنيف
    classification = classify_results(results, query)
    
    # 3. حفظ
    if save:
        filepath = save_results(query, results, classification)
        print(f"✅ النتائج محفوظة: {filepath}")
    
    # 4. تقرير
    report = f"""
╔══════════════════════════════════╗
║     🕵️ تقرير الراصد              ║
╚══════════════════════════════════╝

🔍 الاستفسار: {query}
📊 عدد النتائج: {len(results)}

📋 التصنيف:
{classification}

📎 النتائج:
"""
    for i, r in enumerate(results, 1):
        title = r.get("title", "بدون عنوان")
        url = r.get("url", "بدون رابط")
        content = r.get("content", "")[:300]
        report += f"""
{i}. {title}
   🔗 {url}
   📄 {content}
"""
    
    report += f"""
══════════════════════════════════
🕵️ الراصد - عائلة جنجون
"""
    return report

# ========== واجهة سطر الأوامر ==========
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📋 الأوامر المتاحة:")
        print("  python agent.py search 'عبارة البحث'")
        print("  python agent.py deep 'عبارة البحث'")
    else:
        command = sys.argv[1]
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        
        if command == "search":
            results = search_web(query)
            for i, r in enumerate(results, 1):
                print(f"{i}. {r.get('title', '')}: {r.get('content', '')[:200]}")
        
        elif command == "deep":
            print(deep_search(query))
