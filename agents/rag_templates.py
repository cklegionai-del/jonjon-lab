import os
import chromadb
from ollama import embeddings

TEMPLATES_DIR = os.path.expanduser("~/jonjon-lab/html-templates")
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION = "html_templates"

client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

try:
    client.delete_collection(COLLECTION)
except:
    pass

collection = client.create_collection(COLLECTION)

docs, ids, metas = [], [], []

for root, dirs, files in os.walk(TEMPLATES_DIR):
    # تجاهل node_modules
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'assets']]
    for file in files:
        if file.endswith(('.html', '.css', '.js')) and 'node_modules' not in root:
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if len(content) < 100:
                    continue
                # ناخد أول 3000 حرف كافيين للـ embedding
                chunk = content[:3000]
                rel_path = os.path.relpath(path, TEMPLATES_DIR)
                template_name = rel_path.split('/')[0]
                docs.append(chunk)
                ids.append(rel_path.replace('/', '_').replace('.', '_'))
                metas.append({
                    "path": path,
                    "template": template_name,
                    "file": file,
                    "type": file.split('.')[-1]
                })
                print(f"✅ {rel_path}")
            except Exception as e:
                print(f"❌ {path}: {e}")

print(f"\n📊 {len(docs)} ملف — نحسب الـ embeddings...")

batch_size = 10
for i in range(0, len(docs), batch_size):
    batch_docs = docs[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    batch_metas = metas[i:i+batch_size]
    
    batch_embeddings = []
    for doc in batch_docs:
        resp = embeddings(model="bge-m3", prompt=doc)
        batch_embeddings.append(resp['embedding'])
    
    collection.add(
        documents=batch_docs,
        embeddings=batch_embeddings,
        ids=batch_ids,
        metadatas=batch_metas
    )
    print(f"💾 {min(i+batch_size, len(docs))}/{len(docs)}")

print(f"\n🎉 RAG جاهز! {len(docs)} ملف في ChromaDB")
