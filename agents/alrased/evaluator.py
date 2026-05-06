#!/usr/bin/env python3
"""
📊 مُقيِّم جنجون - أداة تقييم أسبوعية للنظام
تشغلها مرة في اليوم أو الأسبوع لتحليل الأداء
"""
import json, os, sys
from datetime import datetime
from collections import Counter

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "super_reports")
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "alhafez", "data", "learning_memory.json")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def evaluate():
    """تقييم شامل للنظام"""
    memory = load_memory()
    if not memory:
        print("📭 لا توجد بيانات كافية. شغّل السوبرAgent أولاً.")
        return
    
    searches = memory.get("searches", [])
    if not searches:
        print("📭 لا توجد بحوث بعد.")
        return
    
    print(f"""
╔══════════════════════════════════════╗
║     📊 مُقيِّم جنجون                  ║
║     تقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}
╚══════════════════════════════════════╝
""")
    
    # 1. إحصائيات عامة
    total = len(searches)
    scores = [s["score"] for s in searches]
    avg_score = sum(scores) / total
    max_score = max(scores)
    min_score = min(scores)
    
    # اتجاه Score (هل يتحسن؟)
    first_half = searches[:total//2] if total >= 2 else searches
    second_half = searches[total//2:] if total >= 2 else searches
    first_avg = sum(s["score"] for s in first_half) / len(first_half)
    second_avg = sum(s["score"] for s in second_half) / len(second_half)
    trend = "📈 يتحسن" if second_avg > first_avg else "📉 يتراجع" if second_avg < first_avg else "➡️ مستقر"
    
    print(f"📊 إجمالي البحوث: {total}")
    print(f"📊 متوسط Score: {avg_score:.1f}/100")
    print(f"📊 أعلى Score: {max_score} | أدنى Score: {min_score}")
    print(f"📊 اتجاه Score: {trend} ({first_avg:.1f} → {second_avg:.1f})")
    
    # 2. المواضيع الأكثر بحثاً
    topics = [s["query"][:60] for s in searches]
    topic_words = []
    for t in topics:
        topic_words.extend(t.lower().split())
    common_words = Counter(topic_words).most_common(10)
    print(f"\n🔍 الكلمات الأكثر بحثاً:")
    for word, count in common_words[:5]:
        if len(word) > 3:
            print(f"   • {word}: {count} مرة")
    
    # 3. أفضل المصادر
    sources = memory.get("reliable_sources", {})
    if sources:
        print(f"\n📎 أفضل المصادر:")
        sorted_sources = sorted(sources.items(), key=lambda x: x[1].get("count", 0), reverse=True)
        for domain, data in sorted_sources[:5]:
            print(f"   • {domain}: {data.get('count', 0)} مرة (Score متوسط: {data.get('total_score', 0) / max(data.get('count', 1), 1):.0f})")
    
    # 4. توصيات
    print(f"\n💡 توصيات:")
    if avg_score < 70:
        print("   ⚠️ Score منخفض. جرب: تحسين استفسارات البحث، إضافة مصادر جديدة.")
    if max_score - min_score > 40:
        print("   ⚠️ تباين كبير في Scores. حلل أسباب النجاح والفشل.")
    if trend == "📉 يتراجع":
        print("   ⚠️ Score يتراجع. راجع التكتيكات المستخدمة مؤخراً.")
    if avg_score >= 80:
        print("   ✅ أداء ممتاز. استمر في نفس النهج.")
    
    # 5. توصية أسبوعية
    if total >= 5:
        recent = searches[-5:]
        recent_avg = sum(s["score"] for s in recent) / 5
        print(f"\n📅 آخر 5 بحوث: متوسط {recent_avg:.1f}")
        if recent_avg >= 80:
            print("   🎯 جاهز للإطلاق التجريبي!")
    

if __name__ == "__main__":
    evaluate()
