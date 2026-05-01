#!/usr/bin/env python3
"""
🌳 Tree Search - بحث شجرة عميق
يولد فروعاً، يبحث في كل فرع، يجمع النتائج
"""
import json, os, sys, requests
from datetime import datetime
from urllib.parse import quote

OLLAMA_URL = "http://localhost:11434/api/generate"
SEARXNG_URL = "http://localhost:8080/search?format=json&q="
DATA_DIR = os.path.join(os.path.dirname(__file__), "tree_reports")

os.makedirs(DATA_DIR, exist_ok=True)

def ask_model(model, prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": model, "prompt": prompt, "stream": False
    })
    if response.status_code == 200:
        return response.json().get("response", "")
    return ""

def search_web(query, num_results=5):
    try:
        url = SEARXNG_URL + quote(query)
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json().get("results", [])[:num_results]
    except:
        pass
    return []

# ========== 1. توليد الفروع ==========
def generate_branches(topic):
    """يولد 3-5 فروع من الموضوع الرئيسي"""
    print(f"🌳 توليد فروع من: {topic}")
    
    prompt = f"""Generate 4 search branches from this topic: "{topic}"
Each branch should be a specific sub-topic for deep research.
Return ONLY valid JSON:
{{
  "branches": [
    "branch 1: specific subtopic",
    "branch 2: specific subtopic",
    "branch 3: specific subtopic",
    "branch 4: specific subtopic"
  ]
}}"""
    result = ask_model("gpt-oss:20b", prompt)
    result = result.replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(result)
        branches = data.get("branches", [])
        print(f"   ✅ {len(branches)} فروع")
        return branches
    except:
        # Fallback
        return [f"{topic} technology", f"{topic} market", f"{topic} future", f"{topic} challenges"]

# ========== 2. بحث في فرع ==========
def search_branch(branch, depth=1):
    """يبحث في فرع ويعيد ملخصاً"""
    indent = "  " * depth
    print(f"{indent}🔍 [{depth}] {branch}")
    
    results = search_web(branch, 5)
    
    if not results:
        return {"branch": branch, "summary": "لم توجد نتائج", "key_points": []}
    
    # تلخيص النتائج
    text = "\n".join([f"- {r.get('title', '')}: {r.get('content', '')[:200]}" for r in results[:3]])
    
    prompt = f"""Summarize these search results about "{branch}". Return JSON:
{{
  "summary": "2-3 sentence summary in English",
  "key_points": ["point 1", "point 2", "point 3"],
  "sources": ["source 1", "source 2"]
}}
Results: {text[:3000]}"""
    
    result = ask_model("gpt-oss:20b", prompt)
    result = result.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(result)
    except:
        return {"branch": branch, "summary": result, "key_points": []}

# ========== 3. البحث العميق (Tree Search) ==========
def tree_search(topic, max_depth=2):
    """البحث الشجري الكامل"""
    print(f"""
╔══════════════════════════════════════╗
║     🌳 Tree Search - بحث شجرة عميق   ║
║     الموضوع: {topic[:50]}
╚══════════════════════════════════════╝
""")
    
    # المرحلة 1: توليد الفروع
    branches = generate_branches(topic)
    
    # المرحلة 2: البحث في كل فرع
    results = {}
    for branch in branches:
        print(f"\n🌿 فرع: {branch}")
        results[branch] = search_branch(branch)
    
    # المرحلة 3: تجميع التقرير النهائي
    print(f"\n📝 تجميع التقرير النهائي...")
    
    final_report = generate_final_report(topic, results)
    
    # حفظ
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(DATA_DIR, f"tree_{timestamp}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_report)
    
    print(f"✅ التقرير محفوظ: {filepath}")
    return final_report

# ========== 4. التقرير النهائي ==========
def generate_final_report(topic, results):
    """يجمع كل الفروع في تقرير واحد"""
    
    branches_text = ""
    for branch, data in results.items():
        branches_text += f"\n🌿 {branch}:\n"
        branches_text += f"   ملخص: {data.get('summary', 'لا يوجد')}\n"
        points = data.get('key_points', [])
        for p in points:
            branches_text += f"   • {p}\n"
    
    prompt = f"""Write a comprehensive, detailed report in ARABIC about: "{topic}"

Research from all angles:
{branches_text[:5000]}

The report must include:
1. 📋 Executive Summary
2. 📊 For each branch: detailed analysis
3. 🔗 Cross-branch connections and patterns
4. 💡 Key insights and recommendations
5. 📎 Sources

Make it professional, detailed, and ready for publication. Minimum 500 words."""
    
    return ask_model("qwen2.5:32b", prompt)

# ========== واجهة سطر الأوامر ==========
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🌳 استخدام: python tree_search.py 'موضوع البحث'")
    else:
        query = " ".join(sys.argv[1:])
        report = tree_search(query)
        print("\n" + "="*50)
        print(report)
