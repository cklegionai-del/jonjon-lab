#!/usr/bin/env python3
"""
🤖 بوت تيليجرام - سرب جنجون
يرسل موضوعاً → يشغّل السرب → يرد بالتقرير
"""

import os
import sys
import asyncio
from datetime import datetime

# إضافة مسار السرب
sys.path.append(os.path.dirname(__file__))

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("❌ مكتبة python-telegram-bot غير مثبتة.")
    print("   ثبّتها: pip3 install python-telegram-bot")
    sys.exit(1)

from swarm import swarm_search  # استيراد السرب

# ========== الإعدادات ==========
TOKEN = "8603875332:AAFkPnVoD8zJT4c6KF6wkZ20bcaD5laUUcI"  # ⚠️ استبدل هذا بالتوكن الحقيقي

# ========== الأوامر ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /start"""
    await update.message.reply_text(
        "🐝 أهلاً بك في بوت سرب جنجون!\n\n"
        "أرسل لي أي موضوع، وسأقوم بالبحث والتحليل وأرسل لك تقريراً شاملاً.\n\n"
        "📋 مثال:\n"
        "مستقبل الطاقة الشمسية في الشرق الأوسط\n"
        "آخر تطورات الذكاء الاصطناعي\n"
        "privacy tools comparison\n\n"
        "⏳ التقرير يأخذ 3-5 دقائق.\n"
        "🏛️ سرب جنجون - 8 وكلاء | بحث حي + Tor"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /help"""
    await update.message.reply_text(
        "📋 طريقة الاستخدام:\n\n"
        "1. أرسل أي موضوع تريد البحث عنه\n"
        "2. انتظر 3-5 دقائق\n"
        "3. استلم تقريراً شاملاً\n\n"
        "📊 التقرير يشمل:\n"
        "- ملخص تنفيذي\n"
        "- أبرز الاتجاهات\n"
        "- أهم الحقائق\n"
        "- تناقضات وتحذيرات\n"
        "- توصيات عملية\n"
        "- المصادر الرئيسية\n\n"
        "🐝 8 وكلاء يشتغلون معاً | بحث حي + Tor"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أي رسالة نصية"""
    query = update.message.text.strip()
    
    if not query:
        await update.message.reply_text("❌ أرسل موضوعاً للبحث.")
        return
    
    if len(query) < 5:
        await update.message.reply_text("❌ الموضوع قصير جداً. اكتب موضوعاً أطول.")
        return
    
    # إرسال رسالة "جاري البحث"
    msg = await update.message.reply_text(
        f"🐝 جاري البحث والتحليل...\n"
        f"🔍 الموضوع: {query}\n"
        f"⏳ الوقت المتوقع: 3-5 دقائق\n\n"
        f"🔄 يشتغل 8 وكلاء الآن..."
    )
    
    try:
        # تشغيل السرب
        report = swarm_search(query)
        
        # التقرير قد يكون طويلاً. إذا تجاوز 4000 حرف، نقسمه.
        if len(report) > 4000:
            # إرسال الجزء الأول
            part1 = report[:4000]
            await msg.edit_text(part1)
            
            # إرسال الأجزاء المتبقية
            remaining = report[4000:]
            while remaining:
                part = remaining[:4000]
                remaining = remaining[4000:]
                await update.message.reply_text(part)
        else:
            await msg.edit_text(report)
    
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ: {str(e)[:200]}")

# ========== التشغيل ==========
def main():
    """تشغيل البوت"""
    print("🤖 بوت سرب جنجون يشتغل...")
    
    app = Application.builder().token(TOKEN).build()
    
    # الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت جاهز. أرسل /start في تيليجرام.")
    
    # بدء البوت
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
