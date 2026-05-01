import json
import os
import sys
import requests

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
AGENT_DIR = os.path.dirname(__file__)
MEMORY_DIR = os.path.join(os.path.dirname(AGENT_DIR), "alhafez", "data")

# ========== استدعاء نموذج ==========
def ask_model(model, prompt):
    """يرسل prompt إلى نموذج Ollama ويعيد الرد"""
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    if response.status_code == 200:
        return response.json().get("response", "")
    return f"❌ خطأ: {response.status_code}"

# ========== تصنيف البحث ==========
def classify_paper(paper_text):
    """يحدد مجال البحث: هندسة، طب، فيزياء، كيمياء، مالية، عام"""
    prompt = f"""صنف هذا البحث إلى واحد من المجالات التالية فقط: 
    هندسة، طب، فيزياء، كيمياء، مالية، عام.
    أعد كلمة واحدة فقط.

    البحث:
    {paper_text[:2000]}
    """
    result = ask_model("gpt-oss:20b", prompt).strip()
    return result

# ========== تقييم المنهجية ==========
def evaluate_methodology(paper_text):
    """يقيم المنهجية ويعطي Score من 1-30"""
    prompt = f"""أنت محكم أكاديمي. قيم منهجية هذا البحث.
    أعط Score من 1 إلى 30.
    أجب بهذا الشكل بالضبط:
    SCORE: [رقم]
    REASON: [سبب التقييم بالعربية]

    البحث:
    {paper_text[:3000]}
    """
    result = ask_model("gpt-oss:20b", prompt)
    return result

# ========== تقييم الرياضيات ==========
def evaluate_math(paper_text):
    """يقيم الجانب الرياضي والإحصائي ويعطي Score من 1-25"""
    prompt = f"""أنت خبير رياضي. حلل الجانب الرياضي والإحصائي في هذا البحث.
    هل المعادلات صحيحة؟ هل الإحصاء سليم؟
    أعط Score من 1 إلى 25.
    أجب بهذا الشكل بالضبط:
    SCORE: [رقم]
    REASON: [سبب التقييم بالعربية]

    البحث:
    {paper_text[:3000]}
    """
    result = ask_model("qwen2-math:1.5b", prompt)
    return result

# ========== تقييم الأصالة ==========
def evaluate_originality(paper_text):
    """يقيم أصالة الفكرة ويعطي Score من 1-20"""
    prompt = f"""أنت محكم أكاديمي. قيم أصالة وابتكار هذا البحث.
    هل الفكرة جديدة؟ هل هناك إضافة علمية؟
    أعط Score من 1 إلى 20.
    أجب بهذا الشكل بالضبط:
    SCORE: [رقم]
    REASON: [سبب التقييم بالعربية]

    البحث:
    {paper_text[:3000]}
    """
    result = ask_model("gpt-oss:20b", prompt)
    return result

# ========== تقييم الوضوح ==========
def evaluate_clarity(paper_text):
    """يقيم وضوح العرض ويعطي Score من 1-15"""
    prompt = f"""أنت محكم أكاديمي. قيم وضوح العرض وجودة اللغة في هذا البحث.
    أعط Score من 1 إلى 15.
    أجب بهذا الشكل بالضبط:
    SCORE: [رقم]
    REASON: [سبب التقييم بالعربية]

    البحث:
    {paper_text[:3000]}
    """
    result = ask_model("gpt-oss:20b", prompt)
    return result

# ========== تقييم المراجع ==========
def evaluate_references(paper_text):
    """يقيم المراجع ويعطي Score من 1-10"""
    prompt = f"""أنت محكم أكاديمي. قيم المراجع والمصادر في هذا البحث.
    هل هي كافية؟ حديثة؟ موثوقة؟
    أعط Score من 1 إلى 10.
    أجب بهذا الشكل بالضبط:
    SCORE: [رقم]
    REASON: [سبب التقييم بالعربية]

    البحث:
    {paper_text[:3000]}
    """
    result = ask_model("gpt-oss:20b", prompt)
    return result

# ========== التقييم الطبي (إذا البحث طبي) ==========
def evaluate_medical(paper_text):
    """تقييم طبي إضافي"""
    prompt = f"""أنت طبيب وباحث طبي. قيم الجانب الطبي في هذا البحث.
    هل المعلومات الطبية دقيقة؟ هل التشخيص صحيح؟
    أعط Score إضافي من 1 إلى 10.
    أجب بهذا الشكل بالضبط:
    SCORE: [رقم]
    REASON: [سبب التقييم بالعربية]

    البحث:
    {paper_text[:3000]}
    """
    result = ask_model("medgemma:4b", prompt)
    return result

# ========== استخراج Score من النص ==========
def extract_score(text):
    """يستخرج الرقم من نص التقييم"""
    for line in text.split("\n"):
        if "SCORE:" in line.upper():
            try:
                return int(line.split(":")[1].strip())
            except:
                pass
    return 0

# ========== التقييم الكامل ==========
def full_review(paper_path):
    """يقيم البحث كاملاً ويعيد التقرير النهائي"""
    # قراءة الملف
    if not os.path.exists(paper_path):
        return "❌ الملف غير موجود."
    
    with open(paper_path, "r", encoding="utf-8") as f:
        paper_text = f.read()
    
    print("🔍 جاري تصنيف البحث...")
    category = classify_paper(paper_text)
    print(f"📂 المجال: {category}")
    
    print("📝 جاري تقييم المنهجية...")
    methodology = evaluate_methodology(paper_text)
    score_m = extract_score(methodology)
    
    print("🧮 جاري تقييم الرياضيات...")
    math = evaluate_math(paper_text)
    score_math = extract_score(math)
    
    print("💡 جاري تقييم الأصالة...")
    originality = evaluate_originality(paper_text)
    score_o = extract_score(originality)
    
    print("📖 جاري تقييم الوضوح...")
    clarity = evaluate_clarity(paper_text)
    score_c = extract_score(clarity)
    
    print("📚 جاري تقييم المراجع...")
    references = evaluate_references(paper_text)
    score_r = extract_score(references)
    
    total = score_m + score_math + score_o + score_c + score_r
    medical_bonus = 0
    medical_report = ""
    
    if "طب" in category:
        print("🩺 جاري التقييم الطبي...")
        medical = evaluate_medical(paper_text)
        medical_bonus = extract_score(medical)
        total += medical_bonus
        medical_report = f"""
🩺 التقييم الطبي: {medical_bonus}/10
{medical}
"""
    
    # بناء التقرير
    report = f"""
╔══════════════════════════════════╗
║     🧮 تقرير التحكيم النهائي      ║
╚══════════════════════════════════╝

📂 المجال: {category}

📊 جدول التقييم:
┌────────────────────┬────────┬──────────┐
│ المحور              │ Score  │ الوزن     │
├────────────────────┼────────┼──────────┤
│ المنهجية            │ {score_m}/30  │ 30%      │
│ الرياضيات والإحصاء  │ {score_math}/25  │ 25%      │
│ الأصالة             │ {score_o}/20  │ 20%      │
│ وضوح العرض         │ {score_c}/15  │ 15%      │
│ المراجع             │ {score_r}/10  │ 10%      │
{ "│ التقييم الطبي       │ " + str(medical_bonus) + "/10  │ إضافي    │" if medical_bonus > 0 else "" }
├────────────────────┼────────┼──────────┤
│ المجموع الكلي       │ {total}/100 │ 100%     │
└────────────────────┴────────┴──────────┘

📝 تقييم المنهجية:
{methodology}

🧮 تقييم الرياضيات:
{math}

💡 تقييم الأصالة:
{originality}

📖 تقييم الوضوح:
{clarity}

📚 تقييم المراجع:
{references}
{medical_report}

══════════════════════════════════
"""
    
    # حفظ التقرير
    report_dir = os.path.join(AGENT_DIR, "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_name = os.path.basename(paper_path).replace(".txt", "_report.txt")
    report_path = os.path.join(report_dir, report_name)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ التقرير محفوظ: {report_path}")
    return report

# ========== واجهة سطر الأوامر ==========
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📋 الاستخدام:")
        print("  python agent.py review 'مسار_الملف'")
        print("  python agent.py classify 'مسار_الملف'")
    else:
        command = sys.argv[1]
        
        if command == "review":
            paper_path = sys.argv[2] if len(sys.argv) > 2 else ""
            if paper_path:
                print(full_review(paper_path))
            else:
                print("❌ يرجى تحديد مسار الملف.")
        
        elif command == "classify":
            paper_path = sys.argv[2] if len(sys.argv) > 2 else ""
            if paper_path and os.path.exists(paper_path):
                with open(paper_path, "r") as f:
                    text = f.read()
                print(f"📂 المجال: {classify_paper(text)}")
