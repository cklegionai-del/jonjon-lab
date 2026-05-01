import json
import os
import sys
import requests
from datetime import datetime
from urllib.parse import quote

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
SEARXNG_URL = "http://localhost:8080/search?format=json&q="
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

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

# ========== البحث الحي ==========
def search_web(query, num_results=10):
    """يبحث في الويب باستخدام SearXNG"""
    try:
        url = SEARXNG_URL + quote(query)
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])[:num_results]
    except:
        pass
    return []

# ========== التحليل العميق ==========
def analyze_results(query, results):
    """يحلل النتائج ويعطي تقريراً تحليلياً شاملاً"""
    
    # تجهيز النتائج كنص
    results_text = ""
    for i, r in enumerate(results[:10], 1):
        title = r.get("title", "بدون عنوان")
        content = r.get("content", "")[:300]
        url = r.get("url", "")
        results_text += f"{i}. {title}\n   URL: {url}\n   {content}\n\n"
    
    # 1. التصنيف الذكي
    classify_prompt = f"""حلل هذه النتائج لموضوع: "{query}".
    
    النتائج:
    {results_text[:4000]}
    
    أجب بهذا الشكل بالضبط:
    📊 التصنيف:
    🔴 مهم جداً: (نتيجة أو اثنتان) مع سبب
    🟡 مفيد: (2-3 نتائج) مع سبب
    ⚪ عادي: الباقي
    
    📈 تحليل الاتجاه:
    (ما هي أبرز 3 مواضيع أو اتجاهات تظهر في هذه النتائج؟)
    """
    classification = ask_model("gpt-oss:20b", classify_prompt)
    
    # 2. التلخيص العميق
    summary_prompt = f"""اكتب ملخصاً تحليلياً شاملاً عن: "{query}" بناءً على نتائج البحث.
    اكتب 3-5 فقرات بالعربية.
    غطِّ: أبرز المعلومات، الاختلافات بين المصادر، أي تناقضات، ومعلومات قد تكون مفقودة.
    """
    summary = ask_model("qwen2.5:32b", summary_prompt)
    
    # 3. استخراج الكيانات (أشخاص، أماكن، أحداث)
    entities_prompt = f"""استخرج من هذه النتائج:
    - أسماء أشخاص مهمة
    - أسماء أماكن
    - تواريخ أو أحداث
    - أرقام أو إحصائيات
    النتائج:
    {results_text[:3000]}
    """
    entities = ask_model("gpt-oss:20b", entities_prompt)
    
    return {
        "classification": classification,
        "summary": summary,
        "entities": entities
    }

# ========== المقارنة بين مصادر ==========
def compare_sources(results):
    """يقارن بين المصادر المختلفة ويكشف التناقضات"""
    sources = []
    for r in results[:5]:
        sources.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", "")[:200]
        })
    
    compare_prompt = f"""قارن بين هذه المصادر الإخبارية. هل هناك:
    1. اتفاق في المعلومات؟
    2. تناقضات أو اختلافات؟
    3. مصدر يبدو أكثر مصداقية من غيره؟
    4. معلومات حصرية في مصدر دون آخر؟
    
    المصادر:
    {json.dumps(sources, ensure_ascii=False, indent=2)[:3000]}
    
    أجب بالعربية.
    """
    return ask_model("gpt-oss:20b", compare_prompt)

# ========== توليد التقرير النهائي ==========
def generate_final_report(query, analysis, comparison):
    """يولد تقريراً نهائياً منسقاً"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"""
╔══════════════════════════════════════════╗
║     🧠 تقرير الراصد الخارق                ║
║     Super Agent Search Report            ║
╚══════════════════════════════════════════╝

📅 التاريخ: {timestamp}
🔍 الموضوع: {query}

{'─' * 50}

📊 التصنيف والاتجاهات:
{analysis.get('classification', 'غير متوفر')}

{'─' * 50}

📝 الملخص التحليلي:
{analysis.get('summary', 'غير متوفر')}

{'─' * 50}

👤 الكيانات المستخرجة (أشخاص، أماكن، أرقام):
{analysis.get('entities', 'غير متوفر')}

{'─' * 50}

⚖️ مقارنة المصادر:
{comparison}

{'─' * 50}

✅ تم التحليل بواسطة: gpt-oss + qwen2.5 + SearXNG
🏛️ الراصد الخارق - عائلة جنجون
"""
    
    # حفظ التقرير
    report_name = f"super_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join(REPORTS_DIR, report_name)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    return report, report_path

# ========== المهمة الكاملة ==========
def super_search(query):
    """ينفذ البحث الكامل: بحث ← تحليل ← مقارنة ← تقرير"""
    print(f"🧠 الراصد الخارق: جاري البحث عن: {query}")
    print("=" * 50)
    
    # 1. البحث
    print("🔍 [1/4] جاري البحث في الويب...")
    results = search_web(query)
    if not results:
        return "❌ لم أجد نتائج."
    print(f"   ✅ وجدت {len(results)} نتيجة.")
    
    # 2. التحليل
    print("📊 [2/4] جاري التحليل العميق...")
    analysis = analyze_results(query, results)
    print("   ✅ اكتمل التحليل.")
    
    # 3. المقارنة
    print("⚖️ [3/4] جاري مقارنة المصادر...")
    comparison = compare_sources(results)
    print("   ✅ اكتملت المقارنة.")
    
    # 4. التقرير
    print("📝 [4/4] جاري توليد التقرير النهائي...")
    report, report_path = generate_final_report(query, analysis, comparison)
    print(f"   ✅ التقرير محفوظ: {report_path}")
    
    return report

# ========== المراقبة الذكية (مقارنة ببحث سابق) ==========
def compare_with_previous(query):
    """يقارن نتائج البحث الحالية بآخر بحث لنفس الموضوع"""
    # البحث عن آخر ملف لنفس الموضوع
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    previous_results = None
    
    for f in sorted(files, reverse=True):
        filepath = os.path.join(DATA_DIR, f)
        with open(filepath, "r") as fp:
            data = json.load(fp)
        if query.lower() in data.get("query", "").lower():
            previous_results = data
            break
    
    if not previous_results:
        return "📭 لا يوجد بحث سابق للمقارنة."
    
    # مقارنة النتائج الحالية بالسابقة
    current_results = search_web(query)
    
    compare_prompt = f"""قارن بين نتائج بحثين عن نفس الموضوع: "{query}".
    
    البحث القديم ({previous_results.get('timestamp')}):
    {json.dumps(previous_results.get('results', [])[:3], ensure_ascii=False)[:2000]}
    
    البحث الجديد:
    {json.dumps([{'title': r.get('title'), 'content': r.get('content', '')[:200]} for r in current_results[:3]], ensure_ascii=False)[:2000]}
    
    أجب بالعربية:
    1. ما الجديد؟
    2. ما الذي تغير؟
    3. ما الذي بقي كما هو؟
    """
    
    return ask_model("gpt-oss:20b", compare_prompt)

# ========== واجهة سطر الأوامر ==========
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════╗
║     🧠 الراصد الخارق - Super Agent       ║
╚══════════════════════════════════════════╝

📋 الأوامر:
  python super_agent.py search 'موضوع البحث'
  python super_agent.py compare 'موضوع'
  python super_agent.py watch 'موضوع'  (قريباً)

📖 أمثلة:
  python super_agent.py search 'آخر أخبار الذكاء الاصطناعي'
  python super_agent.py compare 'أسعار النفط'
""")
    else:
        command = sys.argv[1]
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        
        if command == "search":
            if query:
                print(super_search(query))
            else:
                print("❌ اكتب موضوع البحث.")
        
        elif command == "compare":
            if query:
                print(compare_with_previous(query))
            else:
                print("❌ اكتب موضوع للمقارنة.")
