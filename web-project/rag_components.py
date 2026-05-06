#!/usr/bin/env python3
# rag_ingest.py - إضافة جميع القوالب إلى قاعدة RAG بشكل صحيح

import os
import html2text
from bs4 import BeautifulSoup
import chromadb
from chromadb.utils import embedding_functions
import hashlib

# ========== الإعدادات ==========
TEMPLATES_DIR = os.path.expanduser("~/jonjon-lab/html-templates")
CHROMA_PERSIST_DIR = os.path.expanduser("~/jonjon-lab/chroma_db")

# ========== الاتصال بقاعدة البيانات ==========
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# نموذج التضمين
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3"
)

# حذف المجموعة القديمة وإنشاء جديدة
try:
    client.delete_collection("html_components")
    print("🗑️ تم حذف المجموعة القديمة")
except:
    pass

collection = client.create_collection(
    name="html_components",
    embedding_function=embedding_fn
)
print("✅ تم إنشاء مجموعة جديدة")

# ========== استخراج المكونات من ملف HTML ==========
def extract_components(html_content, file_path, template_name):
    """استخراج أقسام HTML كاملة (header, section, footer, nav, div)"""
    soup = BeautifulSoup(html_content, 'html.parser')
    components = []
    
    # الأقسام الرئيسية التي نريد استخراجها
    tags_to_extract = ['header', 'footer', 'nav', 'section', 'main', 'aside']
    
    # إضافة divs الكبيرة التي تحتوي على class مهم
    for div in soup.find_all('div', class_=True):
        classes = ' '.join(div.get('class', [])).lower()
        important_classes = ['hero', 'container', 'wrapper', 'content', 'grid', 'cards', 'product', 'menu']
        if any(c in classes for c in important_classes):
            tags_to_extract.append(div)
    
    for tag in tags_to_extract:
        if isinstance(tag, str):
            elements = soup.find_all(tag)
        else:
            elements = [tag]
        
        for element in elements:
            # تجاوز الأجزاء الصغيرة جداً
            text = element.get_text(strip=True)
            if len(text) < 50:
                continue
            
            # تحديد نوع المكون
            element_type = element.name
            classes = ' '.join(element.get('class', [])).lower() if element.get('class') else ''
            
            if 'hero' in classes or 'banner' in classes:
                comp_type = 'hero'
            elif 'card' in classes:
                comp_type = 'cards'
            elif element.name == 'nav':
                comp_type = 'navbar'
            elif element.name == 'footer':
                comp_type = 'footer'
            elif 'form' in classes or element.name == 'form':
                comp_type = 'form'
            elif 'grid' in classes or 'row' in classes:
                comp_type = 'grid'
            else:
                comp_type = element.name
            
            # استخراج CSS المرتبط (اختياري)
            css_content = ""
            style_tag = soup.find('style')
            if style_tag and style_tag.string:
                css_content = style_tag.string[:500]
            
            # بناء المحتوى النصي للمكون
            full_content = f"""
[Type: {comp_type}]
[Template: {template_name}]
[Source: {file_path}]

HTML:
{str(element)}

CSS:
{css_content}
"""
            
            # معرف فريد للمكون
            comp_id = hashlib.md5(f"{file_path}_{str(element)[:200]}".encode()).hexdigest()
            
            components.append({
                "id": comp_id,
                "content": full_content,
                "metadata": {
                    "source": file_path,
                    "template": template_name,
                    "type": comp_type
                }
            })
    
    return components

# ========== المعالجة الرئيسية ==========
print(f"📂 البحث في: {TEMPLATES_DIR}")

all_components = []
total_files = 0

for root, dirs, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if not file.endswith('.html'):
            continue
        
        file_path = os.path.join(root, file)
        template_name = os.path.basename(root)
        
        print(f"📄 معالجة: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            components = extract_components(html_content, file_path, template_name)
            
            if components:
                all_components.extend(components)
                print(f"   ✅ استخرج {len(components)} مكوناً")
                total_files += 1
            else:
                print(f"   ⚠️ لا توجد مكونات")
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")

# ========== إضافة جميع المكونات إلى قاعدة البيانات ==========
if all_components:
    print(f"\n📦 إضافة {len(all_components)} مكون إلى قاعدة البيانات...")
    
    # إضافة على دفعات (batch) لتجنب مشاكل الذاكرة
    batch_size = 50
    for i in range(0, len(all_components), batch_size):
        batch = all_components[i:i+batch_size]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["content"] for c in batch],
            metadatas=[c["metadata"] for c in batch]
        )
        print(f"   ✅ تمت إضافة دفعة {i//batch_size + 1}/{(len(all_components)-1)//batch_size + 1}")
    
    print(f"\n🎉 اكتمل! تمت إضافة {collection.count()} مكوناً من {total_files} ملف HTML")
else:
    print("❌ لم يتم العثور على أي مكونات")

# ========== اختبار سريع ==========
print("\n📝 اختبار البحث...")
results = collection.query(query_texts=["hero section"], n_results=3)
print(f"🔍 نتائج البحث عن 'hero section': {len(results['documents'][0])} مكون")
for i, doc in enumerate(results['documents'][0]):
    print(f"   {i+1}. {doc[:100]}...")
