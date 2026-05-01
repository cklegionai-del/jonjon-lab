import json
import os
from datetime import datetime
import requests

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "data")
INDEX_FILE = os.path.join(MEMORY_DIR, "index.json")

# تأكد من وجود مجلد البيانات
os.makedirs(MEMORY_DIR, exist_ok=True)

# ========== تحميل الفهرس ==========
def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_index(index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

# ========== الحفظ ==========
def save_entry(content, category="general", tags=None):
    """يحفظ محتوى في مجلد ويعيد فهرسته"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_{category}.md"
    filepath = os.path.join(MEMORY_DIR, filename)
    
    # كتابة الملف
    full_content = f"# {category.upper()}\nالتاريخ: {timestamp}\nالوسوم: {tags or []}\n\n{content}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    # تضمين المحتوى باستخدام bge-m3
    embedding = get_embedding(content)
    
    # تحديث الفهرس
    index = load_index()
    index.append({
        "filename": filename,
        "category": category,
        "tags": tags or [],
        "timestamp": timestamp,
        "embedding": embedding,
        "preview": content[:200]
    })
    save_index(index)
    
    return f"✅ تم الحفظ: {filename}"

# ========== تضمين النص ==========
def get_embedding(text):
    """يستخدم bge-m3 لتضمين النص"""
    response = requests.post(OLLAMA_URL, json={
        "model": "bge-m3:latest",
        "prompt": text,
        "stream": False
    })
    if response.status_code == 200:
        return response.json().get("response", "")
    return ""

# ========== البحث ==========
def search(query, category=None):
    """يبحث في الذاكرة عن أقرب تطابق"""
    query_embedding = get_embedding(query)
    index = load_index()
    
    if not index:
        return "📭 الذاكرة فارغة. احفظ شيئاً أولاً."
    
    # فلترة حسب الفئة (اختياري)
    if category:
        index = [e for e in index if e["category"] == category]
    
    # بحث بسيط في المعاينة
    results = []
    for entry in index:
        if query.lower() in entry["preview"].lower():
            results.append(entry)
    
    if not results:
        return "❓ لم أجد شيئاً مطابقاً."
    
    # عرض النتائج
    output = f"🔍 وجدت {len(results)} نتيجة:\n\n"
    for i, r in enumerate(results[:5], 1):
        output += f"{i}. [{r['category']}] {r['filename']}\n"
        output += f"   📄 {r['preview'][:100]}...\n\n"
    
    return output

# ========== عرض الملخص ==========
def summary():
    """يعرض ملخصاً لمحتويات الذاكرة"""
    index = load_index()
    if not index:
        return "📭 الذاكرة فارغة."
    
    categories = {}
    for e in index:
        cat = e["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    output = f"🧠 الذاكرة تحتوي على {len(index)} سجل:\n\n"
    for cat, count in categories.items():
        output += f"📂 {cat}: {count} سجل\n"
    
    return output

# ========== واجهة سطر الأوامر ==========
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("📋 الأوامر المتاحة:")
        print("  python agent.py save 'المحتوى' [الفئة] [الوسوم]")
        print("  python agent.py search 'كلمة البحث'")
        print("  python agent.py summary")
    else:
        command = sys.argv[1]
        
        if command == "save":
            content = sys.argv[2] if len(sys.argv) > 2 else ""
            category = sys.argv[3] if len(sys.argv) > 3 else "general"
            tags = sys.argv[4:] if len(sys.argv) > 4 else []
            print(save_entry(content, category, tags))
            
        elif command == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else ""
            category = sys.argv[3] if len(sys.argv) > 3 else None
            print(search(query, category))
            
        elif command == "summary":
            print(summary())
