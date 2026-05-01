import json
import os
import sys
import requests
from datetime import datetime

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FILTER_LOG = os.path.join(DATA_DIR, "filter_log.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_log():
    if os.path.exists(FILTER_LOG):
        with open(FILTER_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_log(log):
    with open(FILTER_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def ask_model(model, prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    if response.status_code == 200:
        return response.json().get("response", "")
    return ""

def filter_news(news_list):
    """
    يستقبل قائمة أخبار ويصنفها:
    🔴 عاجل: مهم جداً
    🟡 مهم: يستحق القراءة
    ⚪ عادي: يمكن تجاهله
    """
    if isinstance(news_list, str):
        news_list = [news_list]
    
    news_text = "\n".join([f"{i+1}. {n}" for i, n in enumerate(news_list)])
    
    prompt = f"""أنت محلل أخبار. صنف هذه الأخبار إلى 3 فئات:
🔴 عاجل: خطير أو يؤثر فوراً
🟡 مهم: يستحق المتابعة
⚪ عادي: أقل أهمية

الأخبار:
{news_text[:3000]}

أعد التصنيف بهذا الشكل:
🔴 عاجل:
- [عنوان]
🟡 مهم:
- [عنوان]
⚪ عادي:
- [عنوان]"""

    result = ask_model("gpt-oss:20b", prompt)
    
    # حفظ في السجل
    log = load_log()
    log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "input_count": len(news_list),
        "classification": result[:500]
    })
    save_log(log)
    
    return result

def summarize_trends():
    """يحلل السجل ويعطي ملخصاً للاتجاهات"""
    log = load_log()
    if not log:
        return "📭 لا يوجد سجل."
    
    recent = log[-10:]
    prompt = f"""حلل آخر {len(recent)} عملية تصنيف أخبار وأعطني:
    1. أبرز 3 مواضيع تكررت
    2. نسبة العاجل/المهم/العادي
    3. توصية للتركيز عليها
    
    البيانات:
    {json.dumps(recent, ensure_ascii=False)[:2000]}"""
    
    return ask_model("gpt-oss:20b", prompt)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📋 الأوامر:")
        print("  python agent.py filter 'الخبر1' 'الخبر2' ...")
        print("  python agent.py trends")
    else:
        command = sys.argv[1]
        
        if command == "filter":
            news = sys.argv[2:]
            if news:
                print("📰 جاري فلترة الأخبار...")
                result = filter_news(news)
                print(result)
        
        elif command == "trends":
            print(summarize_trends())
