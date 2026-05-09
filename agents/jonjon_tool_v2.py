[from typing import Optional, Dict, Any
import os
import re
import time
import json
import logging
from pathlib import Path
import webbrowser

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Tools:
    def __init__(self):
        self.output_dir = Path(os.getenv("JONJON_OUTPUT", "/Users/hichem/jonjon-lab/output"))
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        self.default_model = os.getenv("JONJON_MODEL", "qwen3-coder:30b")
        
    def _sanitize_filename(self, text: str) -> str:
        """ينظف اسم الملف"""
        clean = re.sub(r'[^\w\-_\. ]', '', text)
        return clean.replace(' ', '_').lower()[:50]
    
    def _get_rag_context(self, niche: str, details: str) -> str:
        """يجيب قوالب مشابهة من ChromaDB"""
        try:
            import chromadb
            client = chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
            collection = client.get_or_create_collection("jonjon_memory")
            
            results = collection.query(
                query_texts=[f"{niche} {details}"],
                n_results=3
            )
            
            if not results['documents'][0]:
                return ""
            
            context = "\n\n--- REFERENCE TEMPLATES ---\n"
            for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                context += f"\nTemplate {i+1} ({meta.get('niche', 'unknown')}):\n{doc[:800]}...\n"
            
            return context
            
        except Exception as e:
            logger.warning(f"RAG failed: {e}")
            return ""
    
    def generate_landing_page(self, niche: str, details: Optional[str] = "") -> Dict[str, Any]:
        """
        يبني landing page مع RAG ويحفظها
        
        Returns:
            {
                "success": bool,
                "filepath": str,
                "preview_url": str,
                "html_length": int,
                "time_taken": float,
                "rag_used": bool,
                "error": str (optional)
            }
        """
        start_time = time.time()
        result = {
            "success": False,
            "filepath": "",
            "preview_url": "",
            "html_length": 0,
            "time_taken": 0,
            "rag_used": False,
            "error": ""
        }
        
        try:
            # 1. RAG
            logger.info(f"🔍 RAG search for: {niche}")
            rag_context = self._get_rag_context(niche, details or "")
            result["rag_used"] = bool(rag_context)
            
            # 2. System prompt
            system_prompt = """You are an elite full-stack developer specializing in high-converting landing pages.

CORE RULES:
- Return ONLY complete, valid HTML5
- Embedded CSS in <style> (no external files)
- Mobile-first responsive design
- Semantic HTML with ARIA labels
- SEO meta tags + Open Graph
- Performance optimized (minimal JS)

DESIGN PRINCIPLES:
- Visual hierarchy with clear CTAs
- Trust signals (testimonials, stats)
- Loading states and micro-interactions
- Accessibility compliant (WCAG 2.1 AA)
- Dark mode support (prefers-color-scheme)"""
            
            # 3. Build prompt
            user_prompt = f"""Create a premium landing page for: {niche}

Additional requirements: {details or 'None'}

{rag_context}

OUTPUT REQUIREMENTS:
- Complete HTML5 document
- Embedded CSS with modern design
- Smooth scroll animations
- Contact form with validation
- Social proof section
- Footer with links

Generate production-ready code."""
            
            # 4. Generate
            logger.info(f"🚀 Generating with {self.default_model}...")
            import ollama
            
            response = ollama.chat(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": 0.6,
                    "num_ctx": 8192,
                    "num_predict": 6000
                }
            )
            
            html = response['message']['content']
            html = html.replace("```html", "").replace("```", "").strip()
            
            # 5. Save
            self.output_dir.mkdir(parents=True, exist_ok=True)
            filename = self._sanitize_filename(niche)
            filepath = self.output_dir / f"{filename}.html"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            
            # 6. Save to ChromaDB for future RAG
            try:
                import chromadb
                client = chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
                collection = client.get_or_create_collection("jonjon_memory")
                collection.add(
                    documents=[html],
                    metadatas=[{"niche": niche, "details": details or "", "time": time.time()}],
                    ids=[f"{filename}_{int(time.time())}"]
                )
            except Exception as e:
                logger.warning(f"Failed to save to ChromaDB: {e}")
            
            # 7. Result
            result.update({
                "success": True,
                "filepath": str(filepath),
                "preview_url": f"file://{filepath}",
                "html_length": len(html),
                "time_taken": round(time.time() - start_time, 2)
            })
            
            logger.info(f"✅ Generated: {filepath} ({len(html)} chars in {result['time_taken']}s)")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ Generation failed: {e}")
        
        return result
    
    def generate_and_open(self, niche: str, details: Optional[str] = "") -> str:
        """يبني ويفتح في المتصفح"""
        result = self.generate_landing_page(niche, details)
        
        if result["success"]:
            webbrowser.open(result["preview_url"])
            return f"✅ Generated & opened: {result['filepath']}\n⏱️ Time: {result['time_taken']}s\n📏 Size: {result['html_length']} chars"
        
        return f"❌ Failed: {result['error']}"
    
    def list_templates(self) -> str:
        """يعرض القوالب الموجودة"""
        if not self.output_dir.exists():
            return "No output directory found"
        
        files = sorted(self.output_dir.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not files:
            return "No templates found"
        
        output = f"📁 Templates in {self.output_dir}:\n\n"
        for i, f in enumerate(files[:10], 1):
            size_kb = f.stat().st_size / 1024
            mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(f.stat().st_mtime))
            output += f"{i}. {f.name} ({size_kb:.1f} KB) - {mtime}\n"
        
        return output
    
    def get_template(self, name: str) -> str:
        """يجيب قالب بالاسم"""
        filepath = self.output_dir / f"{name}.html"
        
        if not filepath.exists():
            return f"❌ Template not found: {name}"
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        return f"📄 {name}.html ({len(content)} chars):\n\n{content[:1000]}..."]
