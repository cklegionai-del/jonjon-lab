import json
import os
import sys
from datetime import datetime

# ========== إعدادات ==========
AGENT_DIR = os.path.dirname(__file__)
STATUS_FILE = os.path.join(AGENT_DIR, "status.json")
REPORTS_DIR = os.path.join(AGENT_DIR, "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)

# ========== تحميل/حفظ الحالات ==========
def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "agents": {},
        "stats": {},
        "updates": []
    }

def save_status(data):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== إضافة وكيل ==========
def add_agent(name, status="قيد التطوير"):
    """يسجل وكيلاً جديداً في النظام"""
    data = load_status()
    data["agents"][name] = {
        "status": status,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    data["updates"].append(f"[{datetime.now().strftime('%H:%M')}] ✅ تسجيل وكيل جديد: {name} - {status}")
    save_status(data)
    return f"✅ تم تسجيل الوكيل: {name} ({status})"

# ========== تحديث حالة وكيل ==========
def update_agent(name, new_status):
    """يغير حالة وكيل"""
    data = load_status()
    if name in data["agents"]:
        old = data["agents"][name]["status"]
        data["agents"][name]["status"] = new_status
        data["agents"][name]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data["updates"].append(f"[{datetime.now().strftime('%H:%M')}] 🔄 {name}: {old} → {new_status}")
        save_status(data)
        return f"🔄 {name}: {old} → {new_status}"
    return f"❌ الوكيل '{name}' غير موجود."

# ========== إحصائية ==========
def add_stat(key, value):
    """يضيف أو يحدث إحصائية"""
    data = load_status()
    data["stats"][key] = value
    save_status(data)
    return f"📊 {key}: {value}"

# ========== تقرير الحالة ==========
def status_report():
    """يعرض تقريراً كاملاً عن حالة النظام"""
    data = load_status()
    
    agents = data.get("agents", {})
    stats = data.get("stats", {})
    updates = data.get("updates", [])
    
    total = len(agents)
    active = sum(1 for a in agents.values() if a["status"] == "يعمل")
    dev = sum(1 for a in agents.values() if a["status"] == "قيد التطوير")
    off = sum(1 for a in agents.values() if a["status"] == "متوقف")
    
    report = f"""
╔══════════════════════════════════╗
║     📊 تقرير حالة النظام          ║
╚══════════════════════════════════╝

📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🤖 الوكلاء:
┌──────────────────────────────────┐
│ إجمالي الوكلاء: {total}                │
│ ✅ يعمل: {active}                        │
│ 🔧 قيد التطوير: {dev}                   │
│ ⚪ متوقف: {off}                         │
└──────────────────────────────────┘

📋 تفاصيل الوكلاء:
"""
    for name, info in agents.items():
        icon = "🟢" if info["status"] == "يعمل" else "🟡" if info["status"] == "قيد التطوير" else "⚪"
        report += f"  {icon} {name}: {info['status']} (آخر تحديث: {info['last_updated']})\n"
    
    if stats:
        report += f"\n📊 الإحصائيات:\n"
        for k, v in stats.items():
            report += f"  • {k}: {v}\n"
    
    if updates:
        report += f"\n📝 آخر التحديثات:\n"
        for u in updates[-5:]:
            report += f"  {u}\n"
    
    report += "\n══════════════════════════════════\n"
    
    # حفظ التقرير
    report_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_path = os.path.join(REPORTS_DIR, report_name)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    return report

# ========== إحصاء سريع ==========
def quick_stats():
    """أرقام سريعة"""
    data = load_status()
    agents = data.get("agents", {})
    stats = data.get("stats", {})
    
    total_agents = len(agents)
    active = sum(1 for a in agents.values() if a["status"] == "يعمل")
    total_stats = len(stats)
    total_updates = len(data.get("updates", []))
    
    return f"🤖 وكلاء: {active}/{total_agents} يعملون | 📊 إحصائيات: {total_stats} | 📝 تحديثات: {total_updates}"

# ========== واجهة سطر الأوامر ==========
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📋 الأوامر المتاحة:")
        print("  python agent.py add 'اسم الوكيل' 'الحالة'")
        print("  python agent.py update 'اسم الوكيل' 'الحالة الجديدة'")
        print("  python agent.py stat 'مفتاح' 'قيمة'")
        print("  python agent.py report")
        print("  python agent.py quick")
    else:
        command = sys.argv[1]
        
        if command == "add":
            name = sys.argv[2] if len(sys.argv) > 2 else ""
            status = sys.argv[3] if len(sys.argv) > 3 else "قيد التطوير"
            print(add_agent(name, status))
        
        elif command == "update":
            name = sys.argv[2] if len(sys.argv) > 2 else ""
            status = sys.argv[3] if len(sys.argv) > 3 else "يعمل"
            print(update_agent(name, status))
        
        elif command == "stat":
            key = sys.argv[2] if len(sys.argv) > 2 else ""
            value = sys.argv[3] if len(sys.argv) > 3 else ""
            print(add_stat(key, value))
        
        elif command == "report":
            print(status_report())
        
        elif command == "quick":
            print(quick_stats())
