#!/usr/bin/env python3
"""
🤖 بوت جنجون - نسخة محسنة
- بحث أعمق (10-15 مصدر حسب صعوبة السؤال)
- تفكير منطقي قبل كل بحث
- ذاكرة متعلمة
"""
import os, sys, asyncio, requests, re, json
from urllib.parse import quote
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8603875332:AAFkPnVoD8zJT4c6KF6wkZ20bcaD5laUUcI"
OLLAMA_URL = "http://localhost:11434/api/generate"
SEARXNG_URL = "http://localhost:8080/search?format=json&q="

# النماذج
FAST_MODEL = "qwen3:8b"
SMART_MODEL = "qwen2.5:32b"
LOGIC_MODEL = "gpt-oss:20b"

# ذاكرة المحادثة
chat_memory = {}
# ذاكرة التعلم (بسيطة)
learning_memory = {"successful_queries": {}, "total_searches": 0}

def get_memory(user_id):
    if user_id not in chat_memory:
        chat_memory[user_id] = []
    return chat_memory[user_id]

def add_to_memory(user_id, role, text):
    memory = get_memory(user_id)
    memory.append({"role": role, "text": text[:500]})
    if len(memory) > 15:
        memory.pop(0)

def ask_model(model, prompt, timeout=60):
    """استدعاء نموذج محلي"""
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        print(f"خطأ في {model}: {e}")
    return ""

def estimate_difficulty(query):
    """تقدير صعوبة السؤال (1-10)"""
    easy_words = ["السلام", "كيف", "ما هو", "من", "متى"]
    hard_words = ["حلل", "قارن", "اشرح بالتفصيل", "لماذا", "كيف يعمل", "آلية"]
    
    score = 1
    for w in easy_words:
        if w in query.lower():
            score = max(score, 2)
    for w in hard_words:
        if w in query.lower():
            score = min(10, score + 3)
    
    # الأسئلة الطويلة = أصعب
    if len(query) > 100:
        score += 2
    
    return min(10, max(1, score))

def determine_num_sources(difficulty):
    """تحديد عدد المصادر حسب الصعوبة"""
    if difficulty <= 3:
        return 5
    elif difficulty <= 6:
        return 10
    else:
        return 15

def logical_preprocessing(query, difficulty):
    """طبقة المنطق: تحليل السؤال قبل البحث"""
    if difficulty < 4:
        return {"search_queries": [query], "key_aspects": [], "priority": "سرعة"}
    
    prompt = f"""حلل هذا السؤال وحدد:
السؤال: {query}

أخرج JSON فقط:
{{
  "search_queries": ["استفسار بحث 1", "استفسار بحث 2", "استفسار بحث 3"],
  "key_aspects": ["جانب مهم 1", "جانب مهم 2"],
  "priority": "أي جانب أهم؟"
}}"""
    
    result = ask_model(LOGIC_MODEL, prompt, timeout=30)
    try:
        # تنظيف النتيجة
        result = result.replace("```json", "").replace("```", "").strip()
        return json.loads(result)
    except:
        return {"search_queries": [query], "key_aspects": [], "priority": "عام"}

def search_web_advanced(query, num_sources=10):
    """بحث متقدم بعدة استراتيجيات"""
    all_results = []
    
    # استراتيجية 1: SearXNG
    try:
        r = requests.get(SEARXNG_URL + quote(query), timeout=15)
        if r.status_code == 200:
            results = r.json().get("results", [])[:num_sources]
            for res in results:
                all_results.append({
                    "title": res.get("title", ""),
                    "content": res.get("content", ""),
                    "url": res.get("url", ""),
                    "source": "searxng"
                })
    except:
        pass
    
    # استراتيجية 2: Google fallback
    if len(all_results) < num_sources:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r = requests.get(f"https://www.google.com/search?q={quote(query)}", headers=headers, timeout=10)
            if r.status_code == 200:
                titles = re.findall(r'<h3[^>]*>(.*?)</h3>', r.text, re.DOTALL)
                for i, t in enumerate(titles[:num_sources]):
                    clean_title = re.sub(r'<[^>]+>', '', t)
                    all_results.append({
                        "title": clean_title,
                        "content": "",
                        "url": f"https://google.com/search?q={quote(query)}",
                        "source": "google"
                    })
        except:
            pass
    
    return all_results[:num_sources]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **جنجون AI - النسخة المحسنة**\n\n"
        "✅ بحث أعمق (حسب صعوبة السؤال)\n"
        "✅ تفكير منطقي قبل البحث\n"
        "✅ ذاكرة تتعلم من التجارب\n\n"
        "📝 **الأوامر:**\n"
        "• `/search موضوع` → بحث عميق (4 فروع، 8 وكلاء)\n"
        "• `/deep سؤال` → بحث موسع (15 مصدر)\n"
        "• `/stats` → إحصائيات النظام\n\n"
        "_أي سؤال عادي سأبحث عنه تلقائياً!_",
        parse_mode="Markdown"
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بحث عميق باستخدام SUPER AGENT"""
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text("❌ مثال: `/search الذكاء الاصطناعي`")
    
    msg = await update.message.reply_text(f"🧠 **بحث عميق:** {query}\n⏳ جاري التحليل والبحث...")
    try:
        from super_agent_final import super_search
        report, score, path = super_search(query)
        await msg.edit_text(f"📊 **الجودة:** {score}/100\n\n{report[:3800]}")
        remaining = report[3800:]
        while remaining:
            await update.message.reply_text(remaining[:4000])
            remaining = remaining[4000:]
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)[:200]}")

async def deep_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بحث موسع (15 مصدر)"""
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text("❌ مثال: `/deep تغير المناخ`")
    
    msg = await update.message.reply_text(f"🔍 **بحث موسع:** {query}\n⏳ 15 مصدر...")
    
    # بحث عميق بـ 15 مصدر
    results = search_web_advanced(query, 15)
    
    if not results:
        return await msg.edit_text("❌ لا توجد نتائج")
    
    # بناء السياق
    context_text = "\n".join([f"- {r['title']}: {r['content'][:300]}" for r in results])
    
    prompt = f"""بناءً على هذه المصادر الـ {len(results)}، أجب عن: {query}

المصادر:
{context_text[:4000]}

أجب بالعربية بشكل مفصل. اذكر معلومات محددة من المصادر. إذا كانت المعلومات غير كافية، قل ذلك بصراحة."""
    
    answer = ask_model(SMART_MODEL, prompt, timeout=90)
    
    # إضافة المصادر
    answer += f"\n\n📎 **المصادر المستخدمة:** {len(results)}"
    for i, r in enumerate(results[:5]):
        if r['url']:
            answer += f"\n{i+1}. {r['title'][:80]}"
    
    await msg.edit_text(answer[:4000])

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات البوت"""
    stats_text = f"""📊 **إحصائيات جنجون AI**

🔄 **المحادثات النشطة:** {len(chat_memory)}
🧠 **النماذج:**
   • سريع: `{FAST_MODEL}`
   • ذكي: `{SMART_MODEL}`
   • منطق: `{LOGIC_MODEL}`

🌐 **البحث:** متعدد المصادر (حتى 15)
📚 **الذاكرة:** لكل محادثة 15 رسالة

_للحصول على تقرير عميق، استخدم `/search`_"""
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    user_id = update.effective_user.id
    
    if len(query) < 3:
        return await update.message.reply_text("❌ اكتب شيئاً أطول (3 أحرف على الأقل)")
    
    msg = await update.message.reply_text("🤔 **جاري التحليل والبحث...**")
    
    try:
        # 1. تقدير الصعوبة
        difficulty = estimate_difficulty(query)
        
        # 2. تحديد عدد المصادر
        num_sources = determine_num_sources(difficulty)
        
        # 3. المنطق المسبق (للسؤال الصعب فقط)
        strategy = {"search_queries": [query], "key_aspects": []}
        if difficulty >= 5:
            strategy = logical_preprocessing(query, difficulty)
        
        # 4. البحث
        all_results = []
        for sq in strategy["search_queries"][:3]:  # كحد أقصى 3 استفسارات
            results = search_web_advanced(sq, num_sources // len(strategy["search_queries"]) + 2)
            all_results.extend(results)
        
        # إزالة التكرارات
        seen = set()
        unique_results = []
        for r in all_results:
            if r['title'] not in seen:
                seen.add(r['title'])
                unique_results.append(r)
        
        unique_results = unique_results[:num_sources]
        
        if not unique_results:
            return await msg.edit_text("❌ لا توجد نتائج. حاول بصيغة مختلفة.")
        
        # 5. بناء السياق
        web_context = "\n".join([f"**{r['title']}**: {r['content'][:400]}" for r in unique_results[:num_sources]])
        
        # 6. اختيار النموذج حسب الصعوبة
        response_model = SMART_MODEL if difficulty >= 6 else FAST_MODEL
        
        # 7. تحضير البرومبت
        memory = get_memory(user_id)
        history = "\n".join([f"{m['role']}: {m['text'][:200]}" for m in memory[-8:]])
        add_to_memory(user_id, "مستخدم", query)
        
        prompt = f"""**محادثة سابقة:**
{history}

**معلومات من {len(unique_results)} مصدر:**
{web_context[:3500]}

**السؤال:** {query}
**الجوانب المهمة حسب التحليل:** {', '.join(strategy.get('key_aspects', []))}

**أجب بالعربية:**
- استخدم معلومات محددة من المصادر
- اذكر تفاصيل دقيقة (أرقام، تواريخ، أسماء)
- إذا كانت المعلومات غير كافية، أخبرني بصراحة
- لا تذكر "وفقاً للمصادر" بشكل متكرر"""
        
        # 8. الحصول على الإجابة
        answer = ask_model(response_model, prompt, timeout=90)
        
        if not answer:
            answer = "عذراً، حدث خطأ في معالجة طلبك."
        
        # 9. إضافة بصمة المصادر
        answer += f"\n\n📚 **المصادر:** {len(unique_results)}"
        
        # 10. تذكر الإجابة
        add_to_memory(user_id, "البوت", answer[:300])
        
        # 11. تحديث الذاكرة المتعلمة
        learning_memory["total_searches"] += 1
        key = strategy.get("priority", "عام")
        if key not in learning_memory["successful_queries"]:
            learning_memory["successful_queries"][key] = 0
        learning_memory["successful_queries"][key] += 1
        
        # 12. إرسال الرد
        await msg.edit_text(answer[:4000])
        
        # 13. إعلام بالصعوبة (اختياري)
        if difficulty >= 8:
            await update.message.reply_text(f"ℹ️ سؤال عميق (صعوبة {difficulty}/10) - استخدمت {len(unique_results)} مصدر")
            
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)[:200]}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("deep", deep_search))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت المحسن جاهز!")
    print("   - البحث التكيفي (5-15 مصدر)")
    print("   - المنطق المسبق للأسئلة الصعبة")
    print("   - 3 نماذج حسب الحاجة")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
