#!/usr/bin/env python3
"""
🎓 Professor Researcher - نظام البحث العميق الاحترافي
"""
import os, sys, json, requests, re, time
from datetime import datetime
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== الإعدادات ====================
TOKEN = "8603875332:AAFkPnVoD8zJT4c6KF6wkZ20bcaD5laUUcI"
OLLAMA_URL = "http://localhost:11434/api/generate"
SEARXNG_URL = "http://localhost:8080/search?format=json&q="
REPORTS_DIR = "/Users/hichem/jonjon-lab/agents/alrased/super_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

# النماذج
MODEL_FAST = "qwen3:8b"
MODEL_SMART = "qwen2.5:32b"
MODEL_LOGIC = "gpt-oss:20b"
MODEL_CODER = "qwen3-coder:30b"

# ==================== البحث المتقدم ====================
def search_deep(query, num=25):
    """بحث عميق في عدد كبير من المصادر"""
    results = []
    
    # 1. البحث عبر SearXNG
    try:
        r = requests.get(SEARXNG_URL + quote(query), timeout=20)
        if r.status_code == 200:
            data = r.json()
            for res in data.get("results", [])[:num]:
                results.append({
                    "title": res.get("title", ""),
                    "content": res.get("content", "")[:600],
                    "url": res.get("url", "")
                })
    except:
        pass
    
    # 2. بحث إضافي بكلمات مختلفة
    if len(results) < num:
        variations = [f"تقرير {query}", f"تحليل {query}", f"إحصاءات {query}", f"دراسة {query}"]
        for var in variations[:2]:
            try:
                r = requests.get(SEARXNG_URL + quote(var), timeout=15)
                if r.status_code == 200:
                    for res in r.json().get("results", [])[:5]:
                        if res.get("title") not in [r2["title"] for r2 in results]:
                            results.append({
                                "title": res.get("title", ""),
                                "content": res.get("content", "")[:600],
                                "url": res.get("url", "")
                            })
            except:
                pass
    
    return results[:num]

def extract_numbers_from_results(results):
    """استخراج الأرقام والإحصائيات من النتائج"""
    numbers = []
    for r in results:
        content = r.get("content", "") + " " + r.get("title", "")
        # البحث عن أرقام
        found = re.findall(r'\d+(?:[,\.]\d+)?\s*(?:%|مليون|ألف|مليار|دولار|درجة|متر|كيلو)', content)
        for f in found:
            if f not in numbers:
                numbers.append(f)
        # البحث عن تواريخ
        dates = re.findall(r'\b(?:19|20)\d{2}\b', content)
        for d in dates:
            if d not in numbers:
                numbers.append(d)
    return numbers[:20]

# ==================== وكيل البحث المتخصص ====================
def research_agent(topic, angle, agent_id):
    """وكيل بحث متخصص في زاوية معينة"""
    print(f"   🔍 الوكيل {agent_id}: {angle[:50]}...")
    
    # بحث عميق في هذه الزاوية
    results = search_deep(angle, 20)
    
    if not results:
        return {"id": agent_id, "angle": angle, "findings": [], "numbers": [], "sources": []}
    
    # استخراج الأرقام
    numbers = extract_numbers_from_results(results)
    
    # تحليل النتائج
    context = "\n".join([f"📌 {r['title']}: {r['content'][:400]}" for r in results[:15]])
    
    prompt = f"""أنت باحث أكاديمي محترف. قم بتحليل هذه المصادر حول: {angle}

المصادر:
{context[:3500]}

أخرج JSON فقط:
{{
  "key_findings": [
    "نتيجة مهمة 1 مع تفاصيل محددة",
    "نتيجة مهمة 2 مع أرقام وتواريخ",
    "نتيجة مهمة 3",
    "نتيجة مهمة 4",
    "نتيجة مهمة 5"
  ],
  "critical_numbers": [
    "رقم/إحصائية 1",
    "رقم/إحصائية 2",
    "رقم/إحصائية 3"
  ],
  "summary_paragraph": "فقرة تلخص هذا القسم في 100-150 كلمة"
}}"""

    try:
        analysis = ask_model(MODEL_SMART, prompt, timeout=90)
        analysis = analysis.replace("```json", "").replace("```", "").strip()
        data = json.loads(analysis)
        return {
            "id": agent_id,
            "angle": angle,
            "findings": data.get("key_findings", []),
            "numbers": data.get("critical_numbers", []),
            "summary": data.get("summary_paragraph", ""),
            "sources": [{"title": r["title"], "url": r["url"]} for r in results[:8] if r.get("url")]
        }
    except:
        return {
            "id": agent_id,
            "angle": angle,
            "findings": [f"موضوع {angle} مهم ويحتاج دراسة متعمقة"],
            "numbers": numbers[:5],
            "summary": context[:300],
            "sources": [{"title": r["title"], "url": r.get("url", "")} for r in results[:5]]
        }

# ==================== تحليل السؤال إلى زوايا ====================
def analyze_query_to_angles(query):
    """تحليل السؤال إلى 5 زوايا بحث متخصصة"""
    prompt = f"""أنت أستاذ جامعي متخصص في التحليل. حلل هذا السؤال إلى 5 زوايا بحث متكاملة:

السؤال: {query}

أخرج JSON فقط:
{{
  "main_topic": "الموضوع الرئيسي",
  "angles": [
    "الزاوية الأولى: الجانب التاريخي والتطور",
    "الزاوية الثانية: الجانب الإحصائي والرقمي",
    "الزاوية الثالثة: الجانب الاقتصادي والاجتماعي",
    "الزاوية الرابعة: الجانب المقارن (دول/مناطق)",
    "الزاوية الخامسة: الجانب المستقبلي والتوصيات"
  ],
  "expected_insights": [
    "ما نتوقع اكتشافه في الزاوية 1",
    "ما نتوقع اكتشافه في الزاوية 2",
    "ما نتوقع اكتشافه في الزاوية 3"
  ]
}}"""

    result = ask_model(MODEL_LOGIC, prompt, timeout=60)
    try:
        result = result.replace("```json", "").replace("```", "").strip()
        return json.loads(result)
    except:
        return {
            "main_topic": query,
            "angles": [
                f"ما هو {query}؟",
                f"أرقام وإحصائيات {query}",
                f"تأثير {query} على المجتمع",
                f"مقارنة {query} بين الدول العربية",
                f"مستقبل وتوصيات حول {query}"
            ],
            "expected_insights": []
        }

# ==================== كتابة التقرير الطويل الاحترافي ====================
def write_professional_report(query, agents_results, all_numbers, strategy):
    """كتابة تقرير طويل جداً (4000-8000 كلمة)"""
    
    # تجميع كل النتائج
    all_findings = []
    all_sources = []
    all_summaries = []
    
    for agent in agents_results:
        all_findings.extend(agent.get("findings", []))
        all_sources.extend(agent.get("sources", []))
        all_summaries.append(f"### {agent['angle']}\n{agent.get('summary', '')}\n")
    
    unique_findings = list(dict.fromkeys(all_findings))
    unique_sources = list({s["url"]: s for s in all_sources if s.get("url")}.values())
    unique_numbers = list(dict.fromkeys(all_numbers))
    
    # بناء جدول الأرقام
    numbers_table = "| الرقم/الإحصائية | القيمة | المصدر |\n|-----------------|--------|--------|\n"
    for i, num in enumerate(unique_numbers[:10]):
        numbers_table += f"| {i+1} | {num} | من البحث |\n"
    
    # تجميع الحقائق
    findings_list = "\n".join([f"• {f}" for f in unique_findings[:25]])
    
    # البرومبت الطويل الذي ينتج تقريراً طويلاً
    prompt = f"""أنت أستاذ جامعي محترف، متخصص في كتابة التقارير الأكاديمية الطويلة.

═══════════════════════════════════════════════════════════════
الطلب: اكتب تقريراً شاملاً ومفصلاً جداً (4000-6000 كلمة) عن:
{query}
═══════════════════════════════════════════════════════════════

زوايا البحث المستخدمة:
{chr(10).join([f"{i+1}. {a}" for i, a in enumerate(strategy.get('angles', []))])}

الحقائق المستخرجة ({len(unique_findings)} حقيقة):
{findings_list[:4000]}

الأرقام والإحصائيات الرئيسية:
{chr(10).join([f"• {n}" for n in unique_numbers[:15]])}

ملخصات كل قسم:
{chr(10).join(all_summaries[:3000])}

═══════════════════════════════════════════════════════════════
اكتب التقرير بهذا التنسيق الدقيق، مع تفاصيل واسعة في كل قسم:

# 📋 {query[:80]}

## 📌 الملخص التنفيذي (Executive Summary)
(اكتب 300-500 كلمة تلخص التقرير بالكامل، مع أبرز النتائج والأرقام)

## 📊 الجداول والإحصائيات
{numbers_table}

## 📖 الفصل الأول: الإطار العام والتطور التاريخي
(اكتب 600-800 كلمة مع تفاصيل زمنية وأحداث محددة)

## 📈 الفصل الثاني: التحليل الإحصائي والكمي
(اكتب 600-800 كلمة مع أرقام محددة ونسب مئوية وتواريخ)

## 🌍 الفصل الثالث: التحليل المقارن (حسب المناطق/الدول)
(اكتب 600-800 كلمة مع مقارنات بين دول أو مناطق مختلفة)

## 🏛️ الفصل الرابع: التأثيرات الاقتصادية والاجتماعية
(اكتب 600-800 كلمة مع أمثلة واقعية وحالات دراسية)

## 🔮 الفصل الخامس: التوقعات المستقبلية والتوصيات
(اكتب 500-700 كلمة مع خطوات عملية وتوصيات قابلة للتنفيذ)

## 📚 المصادر والمراجع
(اذكر أهم 15-20 مصدراً مع عناوينها وروابطها)

═══════════════════════════════════════════════════════════════
تعليمات إضافية:
- يجب أن يكون التقرير طويلاً ومفصلاً جداً (هدف 5000 كلمة)
- استخدم لغة عربية أكاديمية محترمة
- أضف أمثلة واقعية وحالات دراسية كلما أمكن
- كل فصل يجب أن يحتوي على أرقام وتواريخ محددة
- لا تختصر، اكتب بتفاصيل عميقة
- استخدم عناوين فرعية داخل كل فصل
═══════════════════════════════════════════════════════════════"""

    report = ask_model(MODEL_SMART, prompt, timeout=180)
    
    # إضافة قسم المصادر إذا لم يكن موجوداً
    if "المصادر" not in report and len(unique_sources) > 0:
        report += f"\n\n## 📚 المصادر والمراجع\n"
        for i, src in enumerate(unique_sources[:15], 1):
            report += f"{i}. **{src.get('title', 'مصدر')[:100]}**\n   🔗 {src.get('url', '')}\n\n"
    
    return report, len(unique_findings), len(unique_sources), len(unique_numbers)

# ==================== مراجعة وتحسين التقرير ====================
def review_and_improve(report, query):
    """نموذج ثانٍ لمراجعة التقرير وتحسينه"""
    print("   📝 مراجعة التقرير وتحسينه...")
    
    prompt = f"""أنت محرر أكاديمي محترف. قم بمراجعة وتحسين هذا التقرير:

السؤال الأصلي: {query}

التقرير الحالي:
{report[:4000]}

اطلع على:
1. هل التقرير طويل بما يكفي؟
2. هل هناك أقسام ناقصة؟
3. هل الأرقام والمعلومات محددة؟

أخرج التقرير المحسن كاملاً، مع إضافة أي تفاصيل ناقصة. اجعل التقرير أطول وأكثر احترافية."""

    improved = ask_model(MODEL_SMART, prompt, timeout=180)
    
    if improved and len(improved) > len(report):
        return improved
    return report

# ==================== حفظ التقرير ====================
def save_complete_report(query, report, score, stats):
    """حفظ التقرير مع كل الإحصائيات"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = re.sub(r'[^\w\s]', '', query)[:40]
    filename = f"{REPORTS_DIR}/professor_{timestamp}_{safe_query}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write(f"🎓 تقرير الأستاذ الباحث\n")
        f.write("="*80 + "\n")
        f.write(f"السؤال: {query}\n")
        f.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"جودة التقرير: {score}/100\n")
        f.write(f"عدد المصادر: {stats['sources']}\n")
        f.write(f"عدد الحقائق: {stats['facts']}\n")
        f.write(f"عدد الأرقام: {stats['numbers']}\n")
        f.write("="*80 + "\n\n")
        f.write(report)
        f.write("\n\n" + "="*80 + "\n")
        f.write("نهاية التقرير\n")
    
    return filename

# ==================== تقييم الجودة ====================
def evaluate_quality(report, query):
    """تقييم جودة التقرير من 0-100"""
    prompt = f"""قيم هذا التقرير من 0-100 بناءً على:
- الطول والتفصيل (ما بين 1000-10000 كلمة)
- دقة المعلومات والأرقام
- التنظيم والتنسيق
- شمولية التغطية

أخرج رقماً فقط (مثال: 85)

السؤال: {query}
التقرير: {report[:2000]}"""

    result = ask_model(MODEL_FAST, prompt, timeout=45)
    try:
        score = int(re.search(r'\d+', result).group())
        return min(100, max(0, score))
    except:
        return 70

# ==================== الوظيفة الرئيسية ====================
def professor_search(query):
    """نظام البحث العميق الكامل"""
    print("\n" + "="*70)
    print(f"🎓 PROFESSOR RESEARCHER - بحث عميق")
    print(f"📋 الموضوع: {query}")
    print("="*70 + "\n")
    
    # 1. تحليل السؤال
    print("📖 [1/6] تحليل السؤال إلى زوايا بحث...")
    strategy = analyze_query_to_angles(query)
    angles = strategy.get("angles", [])
    print(f"   ✅ تم توليد {len(angles)} زاوية بحث")
    
    # 2. تشغيل الوكلاء بالتوازي
    print(f"\n🔍 [2/6] تشغيل {len(angles)} وكيل بحث بالتوازي...")
    agents_results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for i, angle in enumerate(angles[:5]):
            future = executor.submit(research_agent, query, angle, i+1)
            futures[future] = i+1
        
        for future in as_completed(futures):
            result = future.result()
            agents_results.append(result)
            print(f"   ✅ الوكيل {result['id']} اكتمل: {len(result.get('findings', []))} نتيجة")
    
    # 3. تجميع كل الأرقام
    print(f"\n🔢 [3/6] استخراج الأرقام والإحصائيات...")
    all_numbers = []
    for agent in agents_results:
        all_numbers.extend(agent.get("numbers", []))
    all_numbers = list(dict.fromkeys(all_numbers))
    print(f"   ✅ تم استخراج {len(all_numbers)} رقماً/إحصائية")
    
    # 4. كتابة التقرير
    print(f"\n✍️ [4/6] كتابة التقرير الطويل... (قد يستغرق 1-2 دقيقة)")
    report, fact_count, source_count, num_count = write_professional_report(query, agents_results, all_numbers, strategy)
    print(f"   ✅ تم كتابة تقرير بطول {len(report)} حرفاً")
    
    # 5. مراجعة وتحسين
    print(f"\n🔎 [5/6] مراجعة وتحسين التقرير...")
    improved_report = review_and_improve(report, query)
    print(f"   ✅ التقرير المحسن: {len(improved_report)} حرفاً")
    
    # 6. تقييم
    print(f"\n⭐ [6/6] تقييم جودة التقرير...")
    score = evaluate_quality(improved_report, query)
    
    # حفظ
    stats = {"sources": source_count, "facts": fact_count, "numbers": num_count}
    filepath = save_complete_report(query, improved_report, score, stats)
    
    print("\n" + "="*70)
    print(f"✅ اكتمل البحث!")
    print(f"   📊 الجودة: {score}/100")
    print(f"   📚 المصادر: {source_count}")
    print(f"   💡 الحقائق: {fact_count}")
    print(f"   🔢 الأرقام: {num_count}")
    print(f"   📁 المسار: {filepath}")
    print("="*70 + "\n")
    
    final_report = f"""🎓 **تقرير الأستاذ الباحث**

**السؤال:** {query}

**الإحصائيات:**
• جودة التقرير: {score}/100
• عدد المصادر: {source_count}
• عدد الحقائق: {fact_count}
• عدد الأرقام: {num_count}

---

{improved_report[:3900]}

---
⭐ الجودة: {score}/100 | 📚 {source_count} مصدر | 📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}
📁 تم حفظ التقرير الكامل على المكتب"""

    return final_report, score, filepath

# ==================== بوت التيليغرام ====================
def ask_model(model, prompt, timeout=90):
    """استدعاء النماذج المحلية"""
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        print(f"⚠️ خطأ في {model}: {e}")
    return ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎓 **الأستاذ الباحث - Professor Researcher**\n\n"
        "نظام بحث عميق احترافي\n\n"
        "📌 **الأوامر:**\n"
        "• `/prof موضوع البحث` → تقرير طويل جداً (4000-8000 كلمة)\n"
        "• `/deep موضوع` → بحث سريع\n"
        "• `/help` → المساعدة\n\n"
        "📝 **مثال:**\n`/prof أسباب وأبعاد التغير المناخي في العالم العربي`\n\n"
        "⏱️ الوقت المتوقع: 2-4 دقائق\n"
        "📊 النتيجة: تقرير أكاديمي مع جداول وأرقام ومصادر"
    )

async def prof_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text(
            "❌ مثال: `/prof تأثير الذكاء الاصطناعي على الاقتصاد`\n\n"
            "نصائح للحصول على تقرير أفضل:\n"
            "• اجعل السؤال محدداً وواضحاً\n"
            "• أضف كلمات مثل 'تحليل' أو 'أسباب' أو 'تأثيرات'\n"
            "• مثال جيد: `تحليل أسباب ارتفاع الأسعار في تونس 2024`"
        )
    
    msg = await update.message.reply_text(
        f"🎓 **جاري البحث العميق...**\n\n"
        f"📋 {query[:100]}\n\n"
        f"⏳ 5 وكلاء يبحثون بالتوازي\n"
        f"📚 25-30 مصدر لكل وكيل\n"
        f"🕐 الوقت المتوقع: 2-4 دقائق\n\n"
        f"_سيتم إرسال التقرير الكامل عند الانتهاء_"
    )
    
    try:
        report, score, filepath = professor_search(query)
        
        # إرسال التقرير مقسماً
        for i in range(0, len(report), 3900):
            await update.message.reply_text(report[i:i+3900])
        
        # إرسال رابط الملف المحفوظ
        await update.message.reply_text(
            f"📁 **تم حفظ التقرير الكامل على المكتب:**\n"
            f"`{filepath}`\n\n"
            f"⭐ **الجودة:** {score}/100"
        )
        
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)[:300]}\n\nحاول مرة أخرى أو استخدم أمر أبسط مثل `/deep`")

async def deep_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text("مثال: `/deep الذكاء الاصطناعي`")
    
    msg = await update.message.reply_text(f"🔍 بحث سريع: {query}")
    
    try:
        results = search_deep(query, 10)
        if not results:
            return await msg.edit_text("لا توجد نتائج")
        
        context_text = "\n".join([f"• {r['title']}: {r['content'][:200]}" for r in results[:8]])
        prompt = f"أجب بالعربية بشكل مفصل عن:\n{query}\n\nالمصادر:\n{context_text[:3000]}"
        answer = ask_model(MODEL_SMART, prompt, timeout=90)
        await msg.edit_text(answer[:4000] if answer else "لا توجد إجابة")
    except Exception as e:
        await msg.edit_text(f"خطأ: {str(e)[:200]}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎓 **الأستاذ الباحث - الأوامر**\n\n"
        "`/prof موضوع` - تقرير احترافي طويل جداً (5 وكلاء، 25-30 مصدر)\n"
        "`/deep موضوع` - بحث سريع (10-15 مصدر)\n"
        "`/start` - الترحيب\n"
        "`/help` - هذه المساعدة\n\n"
        "**نصائح:**\n"
        "• للتقارير الطويلة، استخدم `/prof`\n"
        "• وقت التقرير الطويل: 2-4 دقائق\n"
        "• يتم حفظ جميع التقارير على المكتب في مجلد super_reports"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prof", prof_command))
    app.add_handler(CommandHandler("deep", deep_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
        lambda u, c: u.message.reply_text("استخدم /prof للسؤال العميق، أو /deep للسؤال السريع، أو /help للمساعدة")))
    
    print("="*60)
    print("🎓 PROFESSOR RESEARCHER - النظام الجديد")
    print("="*60)
    print("الأوامر:")
    print("  /prof <موضوع>  - تقرير احترافي طويل (4000-8000 كلمة)")
    print("  /deep <موضوع>  - بحث سريع")
    print("  /help          - المساعدة")
    print("="*60)
    print(f"📁 حفظ التقارير: {REPORTS_DIR}")
    print("="*60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
