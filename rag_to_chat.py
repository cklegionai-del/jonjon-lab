#!/usr/bin/env python3
import chromadb
import sys

def rag_to_file(query):
    client = chromadb.PersistentClient(path="/Users/hichem/jonjon-lab/chroma_db")
    collection = client.get_collection("html_components")
    result = collection.query(query_texts=[query], n_results=1)
    
    with open("/tmp/rag_template.html", "w") as f:
        f.write(result['documents'][0][0])
    
    print("✅ القالب مسترجع من RAG وحفظ في /tmp/rag_template.html")
    return "/tmp/rag_template.html"

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "قالب HTML لمطعم تونسي"
    rag_to_file(query)
    print("\n📋 الآن في Open Web UI، اكتب: اقرأ الملف /tmp/rag_template.html وطوره")

if __name__ == "__main__":
    main()
