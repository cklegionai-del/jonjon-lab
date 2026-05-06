#!/usr/bin/env python3
# search_rag.py - البحث في قاعدة RAG دون حذف البيانات

import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PERSIST_DIR = os.path.expanduser("~/jonjon-lab/chroma_db")
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3"
)

# الحصول على المجموعة الموجودة
try:
    collection = client.get_collection("html_components")
    print(f"✅ تم العثور على المجموعة، تحتوي على {collection.count()} مكون")
except:
    print("❌ المجموعة غير موجودة، شغل rag_builder.py أولاً")
    collection = None

def search(query, n_results=3):
    # إضافة توجيه Flux قوي
    flux_instruction = """
⚠️ تنبيه مهم: لا تستخدم Unsplash أو picsum أو أي placeholders.
استخدم فقط الصورة التالية: /Users/hichem/Desktop/Flux_Images/flux_dev_upscaled_00138_.png
كرر نفس الصورة لكل صورة في الصفحة.
"""
    
    results = collection.query(query_texts=[query], n_results=n_results)
    if not results['documents'] or len(results['documents'][0]) == 0:
        return flux_instruction + "\n⚠️ لا توجد نتائج إضافية"
    
    context = flux_instruction + "\n--- أمثلة مرجعية ---\n"
    for i, doc in enumerate(results['documents'][0]):
        context += f"\n--- مثال {i+1} ---\n{doc[:800]}\n"
    return context
