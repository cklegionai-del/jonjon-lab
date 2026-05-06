#!/usr/bin/env python3
"""
🎓 DEEP PROFESSOR - التقرير العميق الحقيقي
"""
import os, json, requests, re, time
from datetime import datetime
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = "8603875332:AAFkPnVoD8zJT4c6KF6wkZ20bcaD5laUUcI"
OLLAMA_URL = "http://localhost:11434/api/generate"
SEARXNG_URL = "http://localhost:8080/search?format=json&q="
REPORTS_DIR = "/Users/hichem/jonjon-lab/agents/alrased/super_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def ask_model(model, prompt, timeout=300):
    for attempt in range(2):
        try:
            r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
            if r.status_code == 200:
                return r.json().get("response", "")
        except Exception as e:
            print(f"⚠️ {model} حاول {attempt+1}: {e}")
            if attempt == 0:
                time.sleep(10)
    return ""

def search_massive(query, num=30):
    """بحث شامل في 30 مصدر"""
    results = []
    try:
        r = requests.get(SEARXNG_URL + quote(query), timeout=25)
        if r.status_code == 200:
            for res in r.json().get("results", [])[:num]:
                results.append({
                    "title": res.get("title", ""),
                    "content": res.get("content", "")[:700],
                    "url": res.get("url", "")
                })
    except:
        pass
    return results

def extract_deep_numbers(text):
    """استخراج كل الأرقام والتواريخ"""
    numbers = re.findall(r'\d+(?:[,\.]\d+)?\s*(?:%|مليون|ألف|مليار|دولار|يورو|درهم|دينار|سنة|يوم|شهر)', text)
    dates = re.findall(r'\b(?:19|20)\d{2}\b', text)
    return list(set(numbers + dates))[:20]

def agent_deep_search(angle, query, agent_id):
    """وكيل بحث عميق"""
    print(f"   🔬 الوكيل {agent_id}: {angle[:40]}...")
    results = search_massive(angle, 25)
    
    if not results:
        return {"id": agent_id, "findings": [], "numbers": [], "sources": []}
    
    all_numbers = []
    for r in results:
        all_numbers.extend(extract_deep_numbers(r.get("content", "") + r.get("title", "")))
    
    context = "\n\n".join([f"【المصدر {i+1}】{r['title']}\n{r['content'][:500]}" for i, r in enumerate(results[:15])])
    
    prompt = f"""أنت باحث خبير. حلل بعمق هذه المصادر حول: {angle}

المصادر:
{context[:4000]}

أخرج JSON بهذا الشكل الدقيق:
{{
  "key_findings": [
    "حقيقة رئيسية أولى مع تفاصيل محددة وأرقام",
    "حقيقة رئيسية ثانية مع تواريخ وأسماء",
    "حقيقة رئيسية ثالثة",
    "حقيقة رئيسية رابعة",
    "حقيقة رئيسية خامسة"
  ],
  "critical_numbers": {json.dumps(all_numbers[:10])},
  "detailed_summary": "فقرة موسعة من 150-200 كلمة تلخص هذا القسم بشكل عميق"
}}"""

    analysis = ask_model("qwen3:8b", prompt, timeout=120)
    try:
        analysis = analysis.replace("```json", "").replace("```", "").strip()
        data = json.loads(analysis)
        return {
            "id": agent_id,
            "angle": angle,
            "findings": data.get("key_findings", []),
            "numbers": data.get("critical_numbers", all_numbers[:8]),
            "summary": data.get("detailed_summary", ""),
            "sources": [{"title": r["title"], "url": r["url"]} for r in results[:8] if r.get("url")]
        }
    except:
        return {"id": agent_id, "angle": angle, "findings": [context[:300]], "numbers": all_numbers[:5], "summary": context[:200], "sources": []}

def decompose_query_deep(query):
    """تفكيك السؤال إلى 5 زوايا استراتيجية"""
    prompt = f"""أنت استراتيجي بحث. حلل هذا السؤال إلى 5 زوايا بحث متكاملة وعميقة:

السؤال: {query}

أخرج JSON:
{{
  "angles": [
    "الزاوية الأولى: الجذور التاريخية والتطور (مع تواريخ وأحداث محددة)",
    "الزاوية الثانية: الإحصائيات والأرقام والبيانات الكمية",
    "الزاوية الثالثة: التحليل الاقتصادي والاجتماعي والسياسي",
    "الزاوية الرابعة: المقارنات الدولية (دول عربية وعالمية)",
    "الزاوية الخامسة: التحديات والحلول والتوصيات المستقبلية"
  ]
}}"""

    result = ask_model("gpt-oss:20b", prompt, timeout=60)
    try:
        result = result.replace("```json", "").replace("```", "").strip()
        return json.loads(result).get("angles", [])
    except:
        return [f"ما هو {query}؟", f"أرقام وإحصائيات {query}", f"تأثيرات {query}", f"مقارنة {query}", f"مستقبل {query}"]

def write_deep_report(query, agents_results, all_numbers):
    """كتابة تقرير عميق جداً (5000-8000 كلمة)"""
    
    all_findings = []
    all_sources = []
    summaries = []
    
    for ag in agents_results:
        all_findings.extend(ag.get("findings", []))
        all_sources.extend(ag.get("sources", []))
        summaries.append(f"## {ag['angle']}\n{ag.get('summary', '')}\n")
    
    unique_findings = list(dict.fromkeys(all_findings))[:30]
    unique_sources = list({s["url"]: s for s in all_sources if s.get("url")}.values())
    
    facts_section = "\n".join([f"{i+1}. {f}" for i, f in enumerate(unique_findings)])
    
    numbers_table = "| الرقم/الإحصائية | القيمة |\n|-----------------|--------|\n"
    for n in all_numbers[:15]:
        numbers_table += f"| {n} | مستخرج من المصادر |\n"
    
    prompt = f"""أنت أستاذ جامعي وخبير في كتابة التقارير الأكاديمية الطويلة جداً.

اكتب تقريراً شاملاً وعميقاً جداً (هدف 5000-8000 كلمة) بالعربية الفصحى عن:

# {query}

═══════════════════════════════════════════════════════════════

الحقائق المستخرجة من البحث ({len(unique_findings)} حقيقة):
{facts_section}

الأرقام والإحصائيات الرئيسية:
{chr(10).join([f"• {n}" for n in all_numbers[:15]])}

ملخصات الأقسام:
{chr(10).join(summaries)}

═══════════════════════════════════════════════════════════════

اكتب التقرير بهذا الهيكل الموسع:

# 📋 {query[:80]}

## 📌 الملخص التنفيذي الشامل
(600-800 كلمة تلخص كل أقسام التقرير بأرقام وتواريخ محددة)

## 📊 جدول الأرقام والإحصائيات الأساسية
{numbers_table}

## 📖 الفصل الأول: الخلفية التاريخية والتطور
(800-1000 كلمة مع تواريخ وأحداث محددة وتحليل)

## 📈 الفصل الثاني: التحليل الإحصائي والكمي
(800-1000 كلمة مع أرقام حقيقية ونسب مئوية واتجاهات)

## 🌍 الفصل الثالث: التحليل المقارن (محلياً ودولياً)
(800-1000 كلمة مع مقارنات بين دول ومدن ومناطق)

## 🏛️ الفصل الرابع: الآثار الاقتصادية والاجتماعية
(700-900 كلمة مع حالات دراسية وأمثلة واقعية)

## 💡 الفصل الخامس: التحديات والحلول والتوصيات
(700-900 كلمة مع خطة عمل وتوصيات قابلة للتنفيذ)

## 🔮 الفصل السادس: التوقعات والسيناريوهات المستقبلية
(500-700 كلمة مع سيناريوهات متفائلة ومتشائمة)

## 📚 المراجع والمصادر
(أهم 20-25 مصدراً مع عناوينها)

═══════════════════════════════════════════════════════════════
تعليمات:
- التقرير يجب أن يكون طويلاً جداً وعميقاً جداً
- استخدم لغة أكاديمية محترمة
- اذكر أرقاماً وتواريخ وأسماء محددة في كل فصل
- أضف أمثلة وحالات دراسية
- لا تختصر، اكتب بتفصيل موسع
═══════════════════════════════════════════════════════════════"""

    report = ask_model("qwen2.5:32b", prompt, timeout=300)
    
    if not report or len(report) < 1000:
        prompt2 = f"""اكتب تقريراً مفصلاً بالعربية عن: {query}

الحقائق: {facts_section[:2000]}

التنسيق:
1. ملخص تنفيذي (300 كلمة)
2. تحليل تفصيلي (1000 كلمة مع أرقام)
3. توصيات (200 كلمة)
4. مصادر"""
        report = ask_model("qwen3-coder:30b", prompt2, timeout=180)
    
    if not report:
        report = facts_section + "\n\n(تعذر كتابة التقرير الكامل بسبب المهلة)"
    
    source_section = "\n\n## 📚 المصادر\n"
    for i, src in enumerate(unique_sources[:15], 1):
        source_section += f"{i}. {src.get('title', 'مصدر')[:100]}\n   🔗 {src.get('url', '')}\n"
    
    final_report = report + source_section
    return final_report, len(unique_findings), len(unique_sources), len(all_numbers)

def professor_deep_search(query):
    """البحث العميق الرئيسي"""
    print(f"\n{'='*60}")
    print(f"🎓 DEEP PROFESSOR: {query}")
    print(f"{'='*60}\n")
    
    print("📖 [1/4] تفكيك السؤال إلى 5 زوايا...")
    angles = decompose_query_deep(query)
    print(f"   ✅ {len(angles)} زاوية بحث استراتيجية")
    
    print(f"\n🔬 [2/4] تشغيل 5 وكلاء بحث متوازيين...")
    agents_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(agent_deep_search, a, query, i+1): i+1 for i, a in enumerate(angles[:5])}
        for future in as_completed(futures):
            agents_results.append(future.result())
            print(f"   ✅ وكيل اكتمل")
    
    print(f"\n🔢 [3/4] تجميع الأرقام والإحصائيات...")
    all_numbers = []
    for ag in agents_results:
        all_numbers.extend(ag.get("numbers", []))
    all_numbers = list(dict.fromkeys(all_numbers))[:20]
    print(f"   ✅ {len(all_numbers)} رقماً/إحصائية")
    
    print(f"\n✍️ [4/4] كتابة التقرير العميق... (قد يستغرق 2-3 دقائق)")
    report, facts, sources, nums = write_deep_report(query, agents_results, all_numbers)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = re.sub(r'[^\w\s]', '', query)[:40]
    filepath = f"{REPORTS_DIR}/deep_prof_{timestamp}_{safe_query}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"تقرير عميق: {query}\nالتاريخ: {timestamp}\nالحقائق: {facts}\nالمصادر: {sources}\nالأرقام: {nums}\n\n{report}")
    
    print(f"\n✅ اكتمل! {facts} حقيقة | {sources} مصدر | {nums} رقم")
    print(f"📁 {filepath}\n")
    
    final = f"🎓 **التقرير العميق: {query[:80]}**\n\n{report[:3900]}\n\n---\n⭐ {facts} حقيقة | 📚 {sources} مصدر | 🔢 {nums} رقم\n📁 حفظ التقرير"
    return final, filepath

# ==================== البوت ====================
async def start(update, context):
    await update.message.reply_text(
        "🎓 **DEEP PROFESSOR**\n\n"
        "`/prof سؤال` → تقرير عميق جداً (5000-8000 كلمة، 5 وكلاء، 30 مصدر)\n"
        "`/deep سؤال` → تقرير متوسط (سريع)\n"
        "`/help` → مساعدة"
    )

async def prof_command(update, context):
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text("مثال: `/prof الاستثمار في الذكاء الاصطناعي في تونس`")
    
    msg = await update.message.reply_text(
        f"🎓 **البحث العميق جارٍ...**\n\n"
        f"📋 {query[:100]}\n\n"
        f"⏳ 5 وكلاء يبحثون في 30 مصدراً لكل وكيل\n"
        f"🕐 الوقت المتوقع: 3-5 دقائق\n\n"
        f"_سيتم إرسال التقرير فور اكتماله_"
    )
    
    try:
        report, filepath = professor_deep_search(query)
        for i in range(0, len(report), 3900):
            await update.message.reply_text(report[i:i+3900])
        await update.message.reply_text(f"📁 **حفظ التقرير:**\n`{filepath}`")
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)[:200]}")

async def deep_command(update, context):
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text("مثال: `/deep الذكاء الاصطناعي`")
    
    msg = await update.message.reply_text(f"🔍 بحث سريع: {query}")
    try:
        results = search_massive(query, 12)
        if not results:
            return await msg.edit_text("لا توجد نتائج")
        context_t = "\n".join([f"- {r['title']}" for r in results[:10]])
        prompt = f"أجب بالعربية بشكل مفصل عن:\n{query}\n\nالمصادر:\n{context_t[:2500]}"
        answer = ask_model("qwen3:8b", prompt, timeout=120)
        await msg.edit_text(answer[:4000] if answer else "لا توجد إجابة")
    except Exception as e:
        await msg.edit_text(f"خطأ: {str(e)[:200]}")

async def help_command(update, context):
    await update.message.reply_text(
        "/prof سؤال - تقرير عميق جداً (3-5 دقائق)\n"
        "/deep سؤال - تقرير متوسط (30-60 ثانية)"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prof", prof_command))
    app.add_handler(CommandHandler("deep", deep_command))
    app.add_handler(CommandHandler("help", help_command))
    
    print("="*60)
    print("🎓 DEEP PROFESSOR - التقرير العميق الحقيقي")
    print("="*60)
    print("/prof → 5 وكلاء، 30 مصدر، 5000-8000 كلمة")
    print("/deep → بحث سريع متوسط")
    print("="*60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
