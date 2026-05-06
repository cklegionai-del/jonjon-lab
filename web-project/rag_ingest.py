import os
import html2text
from chromadb import PersistentClient
from chromadb.utils import embedding_functions

print("🚀 بدء إضافة القوالب إلى قاعدة RAG...")

# الاتصال بقاعدة البيانات
client = PersistentClient(path="/Users/hichem/jonjon-lab/chroma_db")
bge_m3_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-m3")
collection = client.get_or_create_collection(name="html_templates", embedding_function=bge_m3_ef)
print("✅ الاتصال بقاعدة البيانات تم بنجاح")

# مجلد القوالب
TEMPLATES_DIR = "/Users/hichem/jonjon-lab/html-templates/landing"
converter = html2text.HTML2Text()
converter.ignore_links = False

count = 0
for root, dirs, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)
            print(f"📄 معالجة: {file_path}")
            
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    html_content = f.read()
                
                clean_text = converter.handle(html_content)
                doc_id = f"{os.path.basename(root)}_{file}"
                
                collection.upsert(
                    ids=[doc_id],
                    documents=[clean_text],
                    metadatas=[{"source": file_path, "category": os.path.basename(root)}]
                )
                count += 1
                print(f"   ✅ تمت الإضافة (ID: {doc_id})")
            except Exception as e:
                print(f"   ❌ خطأ: {e}")

print(f"\n🎉 اكتمل! تمت إضافة {count} ملف HTML إلى قاعدة RAG")
