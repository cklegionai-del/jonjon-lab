"""
مجلس جنجون - CrewAI للمشرف على الوكلاء
يجمع الوكلاء: الحافظ، المُراجع، الراصد، المُترجم، المُدقِّق
"""
import os
import sys
import subprocess
from datetime import datetime

# ========== مسارات الوكلاء ==========
AGENTS_DIR = os.path.join(os.path.dirname(__file__), "agents")
ALHAFEZ = os.path.join(AGENTS_DIR, "alhafez", "agent.py")
ALMURAJE3 = os.path.join(AGENTS_DIR, "almuraje3", "agent.py")
ALRASED = os.path.join(AGENTS_DIR, "alrased", "agent.py")
ALMUTARJIM = os.path.join(AGENTS_DIR, "almutarjim", "agent.py")
ALMUDAQQIQ = os.path.join(AGENTS_DIR, "almudaqiq", "agent.py")

# ========== تشغيل وكيل ==========
def run_agent(agent_path, *args):
    """يشغل وكيل Python ويعيد النتيجة"""
    cmd = ["python3", agent_path] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

# ========== مهام المجلس ==========

def task_search_and_review(query):
    """مهمة: ابحث عن موضوع وراجعه واحفظه"""
    print("=" * 50)
    print(f"🏛️ مجلس جنجون: بحث ومراجعة")
    print(f"📝 الموضوع: {query}")
    print("=" * 50)
    
    # 1. المترجم: ترجمة الاستفسار للإنجليزية
    print("\n🌐 [المُترجم] جاري الترجمة...")
    en_query = run_agent(ALMUTARJIM, "to_en", query)
    print(f"   الترجمة: {en_query}")
    
    # 2. الراصد: البحث
    print("\n🕵️ [الراصد] جاري البحث...")
    search_result = run_agent(ALRASED, "deep", en_query[:200])
    print(search_result[:500] if len(search_result) > 500 else search_result)
    
    # 3. المُدقِّق: تسجيل العملية
    run_agent(ALMUDAQQIQ, "stat", f"آخر بحث", datetime.now().strftime("%H:%M"))
    run_agent(ALMUDAQQIQ, "stat", f"آخر موضوع", query[:50])
    
    # 4. الحافظ: أرشفة
    print("\n🗄️ [الحافظ] جاري الأرشفة...")
    save_msg = run_agent(ALHAFEZ, "save", f"بحث عن: {query}", "searches", "مجلس,بحث")
    print(f"   {save_msg}")
    
    print("\n" + "=" * 50)
    print("✅ المهمة اكتملت.")
    return search_result

def task_review_paper(paper_path):
    """مهمة: راجع بحثاً أكاديمياً"""
    print("=" * 50)
    print(f"🏛️ مجلس جنجون: مراجعة بحث")
    print(f"📄 الملف: {paper_path}")
    print("=" * 50)
    
    # 1. المُراجع: تحليل البحث
    print("\n🧮 [المُراجع] جاري التحليل...")
    review_result = run_agent(ALMURAJE3, "review", paper_path)
    print(review_result)
    
    # 2. المُدقِّق: تسجيل
    run_agent(ALMUDAQQIQ, "stat", f"آخر مراجعة", datetime.now().strftime("%H:%M"))
    run_agent(ALMUDAQQIQ, "stat", f"عدد المراجعات", "+1")
    
    # 3. الحافظ: أرشفة التقرير
    print("\n🗄️ [الحافظ] جاري الأرشفة...")
    save_msg = run_agent(ALHAFEZ, "save", f"مراجعة بحث: {paper_path}", "reviews", "مجلس,مراجعة")
    print(f"   {save_msg}")
    
    print("\n" + "=" * 50)
    print("✅ المراجعة اكتملت.")
    return review_result

def task_status():
    """مهمة: عرض حالة النظام"""
    print("=" * 50)
    print(f"🏛️ مجلس جنجون: تقرير الحالة")
    print("=" * 50)
    
    # المُدقِّق: تقرير
    report = run_agent(ALMUDAQQIQ, "report")
    print(report)
    
    # الحافظ: ملخص
    summary = run_agent(ALHAFEZ, "summary")
    print(f"\n🗄️ [الحافظ]:\n{summary}")
    
    return report

# ========== القائمة الرئيسية ==========
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════╗
║     🏛️ مجلس جنجون - القائد      ║
╚══════════════════════════════════╝

📋 الأوامر:
  python jonjon_council.py search 'موضوع البحث'
  python jonjon_council.py review 'مسار الملف'
  python jonjon_council.py status
  
📖 مثال:
  python jonjon_council.py search 'فوائد الزنجبيل'
  python jonjon_council.py review test_paper.txt
  python jonjon_council.py status
""")
    else:
        command = sys.argv[1]
        
        if command == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else ""
            if query:
                task_search_and_review(query)
        
        elif command == "review":
            path = sys.argv[2] if len(sys.argv) > 2 else ""
            if path:
                task_review_paper(path)
        
        elif command == "status":
            task_status()
