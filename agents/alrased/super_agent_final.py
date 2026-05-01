#!/usr/bin/env python3
"""
🧠 SUPER AGENT النهائي — جنجون
Tree Search (4 فروع) + Swarm (8 وكلاء) + Memory + Telegram + Self-Improvement
"""
import json, os, sys, requests, re
from datetime import datetime
from urllib.parse import quote

# ==================== الإعدادات ====================
OLLAMA_URL = "http://localhost:11434/api/generate"
SEARXNG_URL = "http://localhost:8080/search?format=json&q="
TELEGRAM_TOKEN = "8603875332:AAFkPnVoD8zJT4c6KF6wkZ20bcaD5laUUcI"
TELEGRAM_CHAT_ID = "8209298416"
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "..", "alhafez", "data")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "super_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# ==================== دوال مساعدة ====================
def ask_model(model, prompt):
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=120)
        if r.status_code == 200: return r.json().get("response", "")
    except: pass
    return ""

def search_web(query, num=5):
    # SearXNG
    try:
        r = requests.get(SEARXNG_URL + quote(query), timeout=15)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results: return results[:num]
    except: pass
    # Google fallback
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(f"https://www.google.com/search?q={quote(query)}", headers=headers, timeout=10)
        if r.status_code == 200:
            titles = re.findall(r'<h3[^>]*>(.*?)</h3>', r.text)
            if titles: return [{"title": t, "content": "", "url": f"https://google.com/search?q={quote(query)}"} for t in titles[:num]]
    except: pass
    return []

def send_telegram(text):
    if TELEGRAM_TOKEN == "YOUR_TOKEN_HERE": return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        for i in range(0, len(text), 4000):
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text[i:i+4000]}, timeout=10)
    except: pass

def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()

def save_to_memory(query, report, score):
    try:
        mem_file = os.path.join(MEMORY_DIR, "super_memory.json")
        memory = []
        if os.path.exists(mem_file):
            with open(mem_file, "r", encoding="utf-8") as f:
                memory = json.load(f)
        memory.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "query": query,
            "score": score,
            "preview": report[:500]
        })
        with open(mem_file, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except: pass

def compare_with_previous(query):
    try:
        mem_file = os.path.join(MEMORY_DIR, "super_memory.json")
        if not os.path.exists(mem_file): return ""
        with open(mem_file, "r", encoding="utf-8") as f:
            memory = json.load(f)
        similar = [m for m in memory if any(w in m.get("query","") for w in query.split()[:3])]
        if similar:
            return f"\n\n📚 **مقارنة مع بحوث سابقة:** ({len(similar)} تقرير سابق)\n" + \
                   "\n".join([f"- {m['timestamp']}: {m['query']} (Score: {m['score']})" for m in similar[-3:]])
    except: pass
    return ""
# ==================== 0. طبقة المنطق الفائق ====================
def logical_deconstruction(topic):
    """يفكك الموضوع إلى استفسارات واستراتيجيات بحث ذكية"""
    print("🧠 [0/6] طبقة المنطق: تفكيك الموضوع...")
    prompt = f"""You are a master research strategist. Deconstruct this topic: "{topic}"

Your goal is to find the MAXIMUM amount of information from the MOST UNIQUE sources.

1.  Break the topic into 5 highly specific search queries. Use different angles (technical, financial, political, social, futuristic).
2.  For each query, suggest 2 UNCONVENTIONAL sources where this info might exist (e.g., patent databases, financial reports of specific companies, niche forums, academic paper repositories, onion sites).
3.  Provide 5 keywords in English, French, and German to maximize search results.
4.  Identify 3 potential biases or contradictions we should look for.

Return ONLY valid JSON:
{{
  "search_queries": ["query 1", "query 2", ...],
  "unconventional_sources": ["source 1", ...],
  "multilingual_keywords": ["kw1", "kw2", ...],
  "potential_biases": ["bias 1", ...]
}}"""
    result = ask_model("qwen2.5:32b", prompt)
    try: return json.loads(clean_json(result))
    except: return {"search_queries": [topic], "unconventional_sources": [], "multilingual_keywords": [], "potential_biases": []}


# ==================== 1. توليد الفروع ====================
def generate_branches(topic):
    print("🌳 [1/6] توليد فروع البحث...")
    prompt = f"""Generate 4 specific research branches from: "{topic}". Each branch is a precise search query.
Return ONLY JSON: {{"branches": ["branch 1", "branch 2", "branch 3", "branch 4"]}}"""
    result = ask_model("gpt-oss:20b", prompt)
    try: return json.loads(clean_json(result)).get("branches", [])
    except: return [f"{topic} technology trends", f"{topic} market economy", f"{topic} challenges risks", f"{topic} future predictions"]

# ==================== 2. تحليل فرع ====================
def analyze_branch(branch, depth):
    indent = "  " * depth
    print(f"{indent}🔍 [{depth}/4] {branch}")
    results = search_web(branch, 5)
    if not results:
        return {"branch": branch, "summary": "لا توجد نتائج", "key_facts": [], "math": "", "compare": "", "sources": []}
    
    text = "\n".join([f"- {r.get('title','')}: {r.get('content','')[:200]}" for r in results])
    sources = [{"title": r.get("title",""), "url": r.get("url","")} for r in results[:3]]
    
    # تحليل
    analysis = ask_model("gpt-oss:20b", f"""Analyze about "{branch}". Return JSON:
{{"summary": "2-3 sentences", "key_facts": ["fact1", "fact2", "fact3"]}}
Results: {text[:3000]}""")
    try: data = json.loads(clean_json(analysis))
    except: data = {"summary": analysis, "key_facts": []}
    
    # رياضيات
    nums = re.findall(r'\d+[\.,]?\d*\s?%?', text)
    math_check = ask_model("qwen2-math:1.5b", f"Verify these numbers: {nums[:10]}") if nums else ""
    
    # مقارنة
    compare = ask_model("gpt-oss:20b", f"Compare sources for '{branch}'. Contradictions? Most credible? {text[:2000]}")
    
    return {**data, "math": math_check[:300], "compare": compare[:300], "sources": sources}

# ==================== 3. التقرير النهائي ====================
def generate_final_report(topic, branches_data):
    print("📝 [5/6] كتابة التقرير النهائي...")
    text = json.dumps(branches_data, ensure_ascii=False, indent=2)[:6000]
    
    prompt = f"""Write a professional, structured report in ARABIC about: "{topic}"

Research data from 4 branches: {text}

FORMAT (use Markdown):
# تقرير تحليلي شامل: {topic}

## 📋 ملخص تنفيذي
[5-6 lines covering ALL branches]

## 📊 الفصل 1: {branches_data[0].get('branch','')}
[Analysis + Key facts + Numbers]

## 📊 الفصل 2: {branches_data[1].get('branch','')}
[Analysis + Key facts + Numbers]

## 📊 الفصل 3: {branches_data[2].get('branch','')}
[Analysis + Key facts + Numbers]

## 📊 الفصل 4: {branches_data[3].get('branch','')}
[Analysis + Key facts + Numbers]

## 🔗 الروابط والأنماط المتقاطعة
[Cross-branch connections]

## ⚖️ مقارنة المصادر والتناقضات
[Source comparison + credibility]

## 💡 التوصيات الاستراتيجية
[Actionable recommendations]

## 📎 المصادر والمراجع
[List sources with URLs]

---
*تقرير SUPER AGENT | 🏛️ جنجون | {datetime.now().strftime('%Y-%m-%d')}*
"""
    return ask_model("qwen2.5:32b", prompt)

# ==================== 4. التقييم ====================
def evaluate_report(report, topic):
    print("🧐 [6/6] تقييم الجودة...")
    prompt = f"Rate this report about '{topic}' from 1-100. Return ONLY the number.\n{report[:2000]}"
    result = ask_model("qwen2.5:32b", prompt)
    try: return max(1, min(100, int(re.search(r'\d+', result).group(0))))
    except: return 50

# ==================== 5. المهمة الكاملة ====================
def super_search(topic):
    print(f"""
╔══════════════════════════════════════╗
║     🧠 SUPER AGENT — جنجون           ║
║     Tree + Swarm + Memory + Telegram ║
╚══════════════════════════════════════╝
🔍 الموضوع: {topic}
""")
    send_telegram(f"🧠 SUPER AGENT بدأ\n🔍 {topic}\n⏳ 4 ف × 8 وكلاء...")
    
    # 1. الفروع
        # 0. طبقة المنطق
    strategy = logical_deconstruction(topic)
    
    # 1. الفروع (باستخدام استفسارات المنطق)
    branches = strategy.get("search_queries", [])
    if not branches:  # إذا فشل المنطق، نعود للطريقة القديمة
        branches = generate_branches(topic)
    else:
        print(f"   ✅ استفسارات ذكية: {len(branches)}")
    
    # 2. تحليل كل فرع
    branches_data = []
    for i, branch in enumerate(branches, 1):
        data = analyze_branch(branch, i)
        branches_data.append(data)
    
    # 3. التقرير
    report = generate_final_report(topic, branches_data)
    
    # 4. مقارنة ببحوث سابقة
    previous = compare_with_previous(topic)
    if previous:
        report += previous
    
    # 5. التقييم
    score = evaluate_report(report, topic)
    
    # 6. تحسين إذا لزم
    if score < 80:
        print(f"   ⚠️ Score منخفض ({score}/100). جاري التحسين...")
        report = ask_model("qwen2.5:32b", f"Improve this report. Make it more detailed, structured, and professional in Arabic:\n{report[:4000]}")
        score = evaluate_report(report, topic)
        print(f"   ✅ Score الجديد: {score}/100")
    
    # 7. حفظ
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(REPORTS_DIR, f"super_{timestamp}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# SUPER AGENT Report\nTopic: {topic}\nScore: {score}/100\nDate: {timestamp}\n\n{report}")
    
    # 8. ذاكرة
    save_to_memory(topic, report, score)
    
    # 9. تيليجرام
    telegram_msg = f"🧠 SUPER AGENT\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n🔍 {topic}\n📊 Score: {score}/100\n\n{report[:3800]}"
    send_telegram(telegram_msg)
    
    print(f"\n✅ Score: {score}/100 | 📁 {filepath} | 📤 Telegram | 🗄️ Memory")
    return report, score, filepath

# ==================== CLI ====================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🧠 استخدام: python super_agent_final.py 'موضوع البحث'")
    else:
        query = " ".join(sys.argv[1:])
        report, score, path = super_search(query)
        print(f"\n{'='*60}")
        print(report[:5000])
