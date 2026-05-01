import json
import os
import sys
import requests

# ========== إعدادات ==========
OLLAMA_URL = "http://localhost:11434/api/generate"
N8N_URL = "http://localhost:5678/api/v1/workflows"
N8N_API_KEY = None  # سنضيفه لاحقاً

# ========== القاموس: أنواع العقد في n8n ==========
NODE_TYPES = {
    "schedule": "n8n-nodes-base.scheduleTrigger",
    "http": "n8n-nodes-base.httpRequest",
    "ai": "n8n-nodes-base.openAi",
    "telegram": "n8n-nodes-base.telegram",
    "email": "n8n-nodes-base.emailSend",
    "spreadsheet": "n8n-nodes-base.googleSheets",
    "webhook": "n8n-nodes-base.webhook",
    "filter": "n8n-nodes-base.if",
    "slack": "n8n-nodes-base.slack",
    "whatsapp": "n8n-nodes-base.whatsApp",
}

def ask_model(model, prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    if response.status_code == 200:
        return response.json().get("response", "")
    return ""

def build_workflow(description_ar):
    """يحول الوصف العربي إلى JSON لـ n8n"""
    
    # ترجمة الوصف للإنجليزية (باستخدام نموذج مدمج)
    translate_prompt = f"Translate to English: {description_ar}"
    description_en = ask_model("gpt-oss:20b", translate_prompt)
    
    # توليد JSON
    prompt = f"""You are an n8n expert. Convert this description into an n8n workflow JSON.
Available node types: {json.dumps(NODE_TYPES, indent=2)}

Description: {description_en}

Generate a valid n8n workflow JSON with:
- name
- nodes (with id, name, type, position, parameters)
- connections

Return ONLY the JSON, no explanation."""
    
    workflow_json = ask_model("qwen2.5:32b", prompt)
    
    # حفظ المخرجات
    output_dir = os.path.join(os.path.dirname(__file__), "workflows")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"workflow_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        # تنظيف الـ JSON (إزالة markdown ``` إن وجد)
        workflow_json = workflow_json.replace("```json", "").replace("```", "").strip()
        data = json.loads(workflow_json)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return f"✅ تم بناء سير العمل: {filepath}\n\n📋 الوصف: {description_ar}"
    except:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(workflow_json)
        return f"⚠️ تم حفظ المخرجات لكن بصيغة غير JSON: {filepath}"

if __name__ == "__main__":
    from datetime import datetime
    
    if len(sys.argv) < 2:
        print("📋 الاستخدام:")
        print('  python agent.py build "وصف الأتمتة بالعربية"')
        print('  مثال: python agent.py build "كل صباح ابحث عن أخبار الذكاء الاصطناعي وأرسلها لتلغرام"')
    else:
        command = sys.argv[1]
        if command == "build":
            desc = " ".join(sys.argv[2:])
            if desc:
                print("⚙️ جاري بناء سير العمل...")
                result = build_workflow(desc)
                print(result)
