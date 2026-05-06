#!/usr/bin/env python3
"""
🤖 SUPER BOT - نسخة طبية محسنة
"""
import os, sys, json, requests, re
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

MODEL_FAST = "qwen3:8b"
MODEL_SMART = "qwen2.5:32b"
MODEL_MEDICAL = "medgemma:4b"

def ask_model(model, prompt, timeout=90):
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        print(f"⚠️ خطأ: {e}")
    return ""

def search_web(query, num=10):
    """بحث عام"""
    results = []
    try:
        r = requests.get(SEARXNG_URL + quote(query), timeout=15)
        if r.status_code == 200:
            data = r.json()
            for res in data.get("results", [])[:num]:
                results.append({
                    "title": res.get("title", ""),
                    "content": res.get("content", "")[:500],
                    "url": res.get("url", "")
                })
    except: pass
    return results

def search_medical(query):
    """بحث طبي متخصص"""
    medical_results = []
    
    # 1. البحث في ويكيبيديا العربية (مصدر طبي جيد)
    try:
        wiki_url = f"https://ar.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(query)}&format=json&utf8=1"
        r = requests.get(wiki_url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for res in data.get("query", {}).get("search", [])[:5]:
                medical_results.append({
                    "title": f"Wikipedia: {res.get('title', '')}",
                    "content": res.get("snippet", "").replace("<span class='searchmatch'>", "").replace("</span>", ""),
                    "url": f"https://ar.wikipedia.org/wiki/{quote(res.get('title', ''))}"
                })
    except: pass
    
    # 2. البحث عبر SearXNG
    try:
        r = requests.get(SEARXNG_URL + quote(query), timeout=15)
        if r.status_code == 200:
            data = r.json()
            for res in data.get("results", [])[:8]:
                title = res.get("title", "")
                url = res.get("url", "")
                # فلترة النتائج الطبية فقط
                if any(k in url.lower() for k in ['health', 'medical', 'medicine', 'drug', 'who', 'mayoclinic', 'webmd', 'pubmed']):
                    medical_results.append({
                        "title": title,
                        "content": res.get("content", "")[:400],
                        "url": url
                    })
                elif any(k in title.lower() for k in ['دواء', 'علاج', 'مرض', 'طبي', 'صحي']):
                    medical_results.append({
                        "title": title,
                        "content": res.get("content", "")[:400],
                        "url": url
                    })
    except: pass
    
    return medical_results[:12]

# ==================== أوامر البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Super Bot\n\n"
        "/ask موضوع - تقرير مفصل\n"
        "/deep موضوع - بحث سريع\n"
        "/medical استفسار طبي - بحث في مصادر طبية\n"
        "/help - مساعدة"
    )

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text("مثال: /ask الذكاء الاصطناعي")
    msg = await update.message.reply_text(f"جاري البحث: {query[:60]}")
    try:
        results = search_web(query, 10)
        if not results:
            return await msg.edit_text("لا توجد نتائج")
        context_text = "\n".join([f"- {r['title']}: {r['content'][:300]}" for r in results[:8]])
        prompt = f"أجب بالعربية عن: {query}\n\nالمعلومات:\n{context_text[:3000]}"
        answer = ask_model(MODEL_SMART, prompt, timeout=90)
        await msg.edit_text(answer[:4000] if answer else "لا توجد إجابة")
    except Exception as e:
        await msg.edit_text(f"خطأ: {str(e)[:200]}")

async def deep_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text("مثال: /deep الذكاء الاصطناعي")
    msg = await update.message.reply_text(f"بحث عميق: {query}")
    try:
        results = search_web(query, 15)
        if not results:
            return await msg.edit_text("لا توجد نتائج")
        context_text = "\n".join([f"• {r['title']}: {r['content'][:200]}" for r in results[:10]])
        prompt = f"أجب بالعربية بشكل مفصل:\n{query}\n\nالمصادر:\n{context_text[:3500]}"
        answer = ask_model(MODEL_SMART, prompt, timeout=120)
        await msg.edit_text(answer[:4000] if answer else "لا توجد إجابة")
    except Exception as e:
        await msg.edit_text(f"خطأ: {str(e)[:200]}")

async def medical_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text(
            "🏥 الاستشارات الطبية\n\n"
            "أمثلة:\n"
            "/medical بديل دواء الكورتيزون\n"
            "/medical علاج حساسية القمح\n"
            "/medical أعراض مرض نادر"
        )
        return
    
    msg = await update.message.reply_text(f"🏥 بحث طبي: {query[:80]}\nجاري البحث في المصادر الطبية...")
    
    try:
        # بحث طبي متخصص
        medical_results = search_medical(query)
        
        if not medical_results:
            # جرب البحث العام
            medical_results = search_web(query, 8)
        
        if not medical_results:
            await msg.edit_text(
                "❌ لم أجد معلومات طبية كافية.\n\n"
                "نصائح:\n"
                "• اكتب اسم الدواء أو المرض بالضبط\n"
                "• استشر طبيبك للحصول على معلومات دقيقة\n\n"
                f"سؤالك: {query}"
            )
            return
        
        # بناء النتائج
        sources_text = "\n".join([
            f"📌 {r['title'][:100]}\n   {r['content'][:200]}"
            for r in medical_results[:6]
        ])
        
        prompt = f"""أنت مساعد طبي. استفسار: {query}

المصادر الطبية:
{sources_text[:3000]}

⚠️ أنا للاسترشاد فقط، لست بديلاً عن الطبيب.

أجب بهذا التنسيق البسيط:

【الخلاصة】
(جملة أو جملتين عن الموضوع)

【البدائل/العلاجات المتاحة】
- نقطة
- نقطة

【التوصيات】
- نقطة

【المصادر】
(اذكر عناوين المصادر فقط)"""

        answer = ask_model(MODEL_MEDICAL, prompt, timeout=90)
        
        if not answer or len(answer) < 50:
            # جرب النموذج الذكي
            answer = ask_model(MODEL_SMART, prompt, timeout=90)
        
        if not answer:
            answer = "عذراً، لم أتمكن من تحليل المعلومات. استشر طبيبك المختص."
        
        # إضافة المصادر في النهاية
        sources_list = "\n".join([f"- {r['title'][:80]}" for r in medical_results[:4]])
        final = f"🏥 استشارة طبية\n\nسؤال: {query}\n\n{answer}\n\n---\n📚 تم البحث في {len(medical_results)} مصدر\nاستشر طبيبك قبل أي قرار."
        
        await msg.edit_text(final[:4000])
        
        # حفظ الاستشارة
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{REPORTS_DIR}/medical_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(f"سؤال: {query}\n\n{answer}\n\nمصادر: {len(medical_results)}")
            
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)[:200]}\n\nاستشر طبيبك مباشرة لهذه الحالة.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "الأوامر:\n"
        "/ask موضوع - تقرير مفصل\n"
        "/deep موضوع - بحث عميق\n"
        "/medical سؤال طبي - استشارة طبية\n"
        "/start - ترحيب\n"
        "/help - هذه المساعدة"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("deep", deep_command))
    app.add_handler(CommandHandler("medical", medical_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
        lambda u, c: u.message.reply_text("استخدم /help لرؤية الأوامر")))
    
    print("="*50)
    print("🤖 SUPER BOT جاهز")
    print("الأوامر: /ask , /deep , /medical , /help")
    print("="*50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
