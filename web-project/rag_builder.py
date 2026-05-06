#!/usr/bin/env python3
# rag_builder.py - نظام RAG لتحسين مخرجات HTML

import os
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import hashlib

# إعدادات المسارات
TEMPLATES_DIR = os.path.expanduser("~/jonjon-lab/html-templates")
CHROMA_PERSIST_DIR = os.path.expanduser("~/jonjon-lab/chroma_db")

# إنشاء مجلد الحفظ إذا لم يكن موجوداً
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# الاتصال بـ ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# إنشاء embedding function باستخدام bge-m3 عبر sentence-transformers
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3"
)

# حذف المجموعة القديمة إذا وجدت
try:
    client.delete_collection("html_components")
    print("🗑️ تم حذف المجموعة القديمة")
except:
    pass

# إنشاء مجموعة جديدة
collection = client.create_collection(
    name="html_components",
    embedding_function=embedding_fn
)

print("✅ تم إنشاء مجموعة ChromaDB بنجاح")

def search_similar(query, n_results=3):
    """البحث عن مكونات مشابهة"""
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        print(f"🔍 بحث: '{query}' -> {len(results['documents'][0]) if results['documents'] else 0} نتيجة")
        return results
    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
        return {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}

def get_context_for_prompt(query, n_results=3):
    """الحصول على سياق لإضافته إلى System Prompt"""
    results = search_similar(query, n_results)
    
    if not results['documents'] or len(results['documents'][0]) == 0:
        return ""
    
    context = "\n--- أمثلة مرجعية (استخدم نفس الأسلوب) ---\n"
    
    for i, doc in enumerate(results['documents'][0]):
        if doc and len(doc) > 0:
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            context += f"\n### مثال {i+1} (نوع: {metadata.get('type', 'unknown')})\n"
            context += doc[:1500]
            context += "\n"
    
    return context

def add_test_data():
    """إضافة بيانات تجريبية للاختبار"""
    test_docs = [
        '<header class="hero"><h1>مرحبا بكم في موقعنا</h1><button>ابدأ الآن</button></header>',
        '<div class="cards"><div class="card"><h3>خدمة 1</h3><p>وصف الخدمة</p></div></div>',
        '<nav><a href="#">الرئيسية</a><a href="#">من نحن</a></nav>',
        '<footer><p>جميع الحقوق محفوظة 2025</p></footer>'
    ]
    test_ids = ['hero_1', 'cards_1', 'navbar_1', 'footer_1']
    test_metas = [
        {'type': 'hero', 'source': 'test'},
        {'type': 'cards', 'source': 'test'},
        {'type': 'navbar', 'source': 'test'},
        {'type': 'footer', 'source': 'test'}
    ]
    
    collection.add(ids=test_ids, documents=test_docs, metadatas=test_metas)
    print(f"✅ تم إضافة {len(test_docs)} مكونات تجريبية")

if __name__ == "__main__":
    add_test_data()
    print(f"\n📊 المجموعة تحتوي على {collection.count()} مكون")
    
    # اختبار البحث
    print("\n📝 اختبار البحث...")
    context = get_context_for_prompt("hero welcome banner")
    if context:
        print(context[:500])
    else:
        print("⚠️ لم يتم العثور على نتائج - حاول مرة أخرى")
