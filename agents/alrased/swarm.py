#!/usr/bin/env python3
"""
🐝 سرب جنجون - Swarm للبحث والتحليل
SIL (Swarm Internal Language) Version
الوكلاء يتواصلون مع بعضهم بـ JSON منظم
الترجمة للعربية فقط في الخطوة النهائية
"""

import json, os, sys, requests, re
from datetime import datetime
from urllib.parse import quote

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
SEARXNG_URL = "http://localhost:8080/search?format=json&q="
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
MEMORY_AGENT = os.path.join(os.path.dirname(__file__), "..", "alhafez", "agent.py")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ========== أدوات مساعدة ==========
def ask_model(model, prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": model, "prompt": prompt, "stream": False
    })
    if response.status_code == 200:
        return response.json().get("response", "")
    return ""

def clean_json(text):
    """ينظف مخرجات النموذج لاستخراج JSON صالح"""
    text = text.replace("```json", "").replace("```", "").strip()
    return text

def search_web(query, num_results=10):
    try:
        url = SEARXNG_URL + quote(query)
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return response.json().get("results", [])[:num_results]
    except:
        pass
    return []

# ========== 1. الباحث ==========
def agent_searcher(query):
    print("🔍 [1/7] الباحث: جاري البحث في الويب...")
    results = search_web(query)
    print(f"   ✅ وجد {len(results)} نتيجة")
    return results

# ========== 2. المحلل (SIL JSON) ==========
def agent_analyst(query, results):
    print("📊 [2/7] المحلل: جاري تحليل النتائج (SIL JSON)...")
    text = ""
    for i, r in enumerate(results[:10], 1):
        text += f"{i}. {r.get('title', '')}\n   {r.get('content', '')[:200]}\n\n"
    
    prompt = f"""Analyze search results for: "{query}".
Results: {text[:4000]}

Return ONLY valid JSON. No explanation, no markdown.
Format:
{{
  "trends": [{{"title": "trend name", "detail": "1 sentence", "confidence": 0.0}}],
  "key_facts": ["fact 1", "fact 2", "fact 3", "fact 4", "fact 5"],
  "contradictions": ["any contradiction found"],
  "missing_info": ["what is missing"]
}}"""
    result = ask_model("gpt-oss:20b", prompt)
    result = clean_json(result)
    print("   ✅ اكتمل التحليل")
    return result

# ========== 3. المقارن (SIL JSON) ==========
def agent_comparer(results):
    print("⚖️ [3/7] المقارن: جاري مقارنة المصادر (SIL JSON)...")
    sources = []
    for r in results[:5]:
        sources.append({"title": r.get("title", ""), "content": r.get("content", "")[:200]})
    
    prompt = f"""Compare these sources. Return ONLY valid JSON. No explanation.
{sources[:3000]}

Format:
{{
  "agreements": ["point 1", "point 2"],
  "contradictions": ["point 1", "point 2"],
  "most_credible": "source name and reason",
  "exclusive_info": "any exclusive info found"
}}"""
    result = ask_model("gpt-oss:20b", prompt)
    result = clean_json(result)
    print("   ✅ اكتملت المقارنة")
    return result

# ========== 4. المدقق الرياضي ==========
def agent_math_checker(results):
    print("🧮 [4/7] المدقق الرياضي: جاري تدقيق الأرقام...")
    numbers_found = []
    for r in results[:5]:
        content = r.get("content", "")
        nums = re.findall(r'\d+[\.,]?\d*\s?%?', content)
        numbers_found.extend(nums[:5])
    
    if numbers_found:
        prompt = f"""Verify these numbers. Are they reasonable? Contradictions?
Numbers: {numbers_found}
Return ONLY valid JSON:
{{"reasonable": true/false, "issues": ["issue if any"], "verified": ["number: ok reason"]}}"""
        result = ask_model("qwen2-math:1.5b", prompt)
        result = clean_json(result)
    else:
        result = '{"reasonable": true, "issues": [], "verified": ["no numbers found"]}'
    print("   ✅ اكتمل التدقيق")
    return result

# ========== 5. المترجم ==========
def agent_translator(results):
    print("🌐 [5/7] المترجم: جاري ترجمة المصادر الأجنبية...")
    non_arabic = []
    for r in results[:5]:
        content = r.get("content", "")[:200]
        if not any('\u0600' <= c <= '\u06ff' for c in content):
            non_arabic.append(content)
    
    if non_arabic:
        prompt = f"""Translate to Arabic. Return ONLY valid JSON:
{{"translated": ["text1", "text2"]}}
Texts: {' | '.join(non_arabic[:3])[:2000]}"""
        result = ask_model("gpt-oss:20b", prompt)
        result = clean_json(result)
    else:
        result = '{"translated": ["جميع المصادر بالعربية"]}'
    print("   ✅ اكتملت الترجمة")
    return result

# ========== 6. المحرر (SIL → العربية) ==========
def agent_editor(query, analyst_json, comparison_json, math_json, translation_json):
    print("📝 [6/7] المحرر: جاري كتابة التقرير النهائي بالعربية...")
    prompt = f"""You are a professional report editor.
You will receive structured JSON data from other agents.
Write a comprehensive, professional report in ARABIC about: "{query}".

Analyst JSON: {analyst_json}
Comparison JSON: {comparison_json}
Math Check JSON: {math_json}
Translation JSON: {translation_json}

The report must include:
1. 📋 Executive Summary (3-4 lines)
2. 📊 Top 3 Trends (from analyst JSON trends)
3. 🔑 Key Facts (from analyst JSON key_facts)
4. ⚠️ Contradictions & Warnings (from comparison JSON)
5. 💡 Practical Recommendations
6. 📎 Main Sources

Write in Modern Standard Arabic. Professional. Ready for publication.
Do NOT mention JSON or internal data structures in the report."""
    result = ask_model("qwen2.5:32b", prompt)
    print("   ✅ اكتمل التقرير")
    return result

# ========== 7. المقيِّم (Self-Critique) ==========
def agent_evaluator(report, query):
    print("🧐 [7/7] المقيِّم: جاري تقييم التقرير...")
    prompt = f"""Evaluate this report about "{query}" honestly.
Report: {report[:3000]}

Return ONLY a number between 1 and 100. No explanation. Just the number."""
    result = ask_model("qwen2.5:32b", prompt)
    result = result.strip()
    
    # استخراج الرقم
    try:
        # إذا كان الرد مجرد رقم
        score = int(result)
    except:
        # إذا كان الرد يحتوي على نصوص أخرى
        nums = re.findall(r'\d+', result)
        score = int(nums[0]) if nums else 50
    
    # نضمن أن score بين 1-100
    score = max(1, min(100, score))
    
    # تقييم افتراضي إذا فشل
    evaluation = {
        "score": score,
        "strengths": ["تقرير شامل", "منظم"],
        "weaknesses": [],
        "improvements": []
    }
    
    print(f"   ✅ اكتمل التقييم (Score: {score}/100)")
    return evaluation, score

# ========== 8. الحافظ (أرشفة) ==========
def agent_memory(query, report, evaluation):
    print("🗄️ [الحافظ] جاري الأرشفة...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report_path = os.path.join(REPORTS_DIR, f"swarm_report_{timestamp}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"🔍 الموضوع: {query}\n")
        f.write(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"📊 Score: {evaluation.get('score', 0)}/100\n")
        f.write(f"{'='*60}\n\n")
        f.write(report)
        f.write(f"\n\n{'='*60}\n")
        f.write(f"📊 تقييم الجودة:\n{json.dumps(evaluation, ensure_ascii=False, indent=2)}\n")
    
    os.system(f"python3 {MEMORY_AGENT} save 'سرب: {query}' searches سرب,تحليل")
    
    print(f"   ✅ التقرير محفوظ: {report_path}")
    return report_path

# ========== المهمة الكاملة ==========
def swarm_search(query):
    """يشغّل السرب كاملاً"""
    print(f"""
╔══════════════════════════════════════╗
║     🐝 سرب جنجون - Swarm Search      ║
║     SIL Version                       ║
║     الموضوع: {query[:50]}
╚══════════════════════════════════════╝
""")
    
    # 1-5: البحث والتحليل (كله JSON)
    results = agent_searcher(query)
    if not results:
        return "❌ لم أجد نتائج."
    
    analyst_json = agent_analyst(query, results)
    comparison_json = agent_comparer(results)
    math_json = agent_math_checker(results)
    translation_json = agent_translator(results)
    
    # 6: كتابة التقرير النهائي بالعربية
    report = agent_editor(query, analyst_json, comparison_json, math_json, translation_json)
    
    # 7: التقييم
    evaluation, score = agent_evaluator(report, query)
    
    # إذا Score < 80، نعيد التحسين تلقائياً
    if score < 80:
        print(f"   ⚠️ Score منخفض ({score}/100). جاري التحسين التلقائي...")
        improvement_prompt = f"""Improve this report based on evaluation.
Evaluation: {json.dumps(evaluation, ensure_ascii=False)[:1000]}
Original Report: {report[:2000]}
Rewrite the COMPLETE report in Arabic with all improvements."""
        report = ask_model("qwen2.5:32b", improvement_prompt)
        evaluation, score = agent_evaluator(report, query)
        print(f"   ✅ Score الجديد: {score}/100")
    
    # 8: الأرشفة
    report_path = agent_memory(query, report, evaluation)
    
    # النتيجة النهائية
    final = f"""
╔══════════════════════════════════════════╗
║     🐝 تقرير سرب جنجون النهائي            ║
║     Score: {score}/100                   ║
╚══════════════════════════════════════════╝

{report}

{'─'*50}
📊 تقييم ذاتي: {score}/100
📁 المحفوظ: {report_path}
🏛️ سرب جنجون - 8 وكلاء | SIL Version
"""
    return final

# ========== واجهة سطر الأوامر ==========
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════╗
║     🐝 سرب جنجون - Swarm Search      ║
║     SIL Version                       ║
╚══════════════════════════════════════╝

📋 الاستخدام:
  python swarm.py 'موضوع البحث'

📖 مثال:
  python swarm.py "مستقبل الطاقة الشمسية في الشرق الأوسط"
""")
    else:
        query = " ".join(sys.argv[1:])
        if query:
            print(swarm_search(query))
        else:
            print("❌ اكتب موضوع البحث.")
