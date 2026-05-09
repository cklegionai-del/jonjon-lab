"""
🚀 Asset Factory API + Frontend
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
import json
from pathlib import Path
from datetime import datetime

from database import init_db, get_db, Asset

app = FastAPI(title="Asset Factory API", version="2.1")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

FRONTEND_PATH = Path(__file__).parent.parent

@app.on_event("startup")
def startup():
    init_db()
    print("✅ قاعدة البيانات جاهزة")

# ========== FRONTEND FIRST ==========
@app.get("/", response_class=HTMLResponse)
def home():
    html_path = FRONTEND_PATH / "index.html"
    return html_path.read_text(encoding='utf-8')

# ========== API ==========
@app.post("/api/import")
def import_from_json(db: Session = Depends(get_db)):
    json_path = FRONTEND_PATH / "data" / "assets.json"
    if not json_path.exists():
        raise HTTPException(404, "assets.json غير موجود")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    db.query(Asset).delete()
    count = 0
    for collection in data.get("collections", []):
        for item in collection.get("items", []):
            asset = Asset(id=item["id"], name=item["name"], path=item.get("path", ""),
                relative_path=item.get("relativePath", ""), type=item["type"],
                category=item.get("category", "uncategorized"), source=item.get("source", ""),
                size=item.get("size", ""), size_bytes=item.get("sizeBytes", 0),
                extension=item.get("extension", ""),
                files_count=item.get("filesCount", item.get("totalFiles", 0)),
                modified=datetime.fromisoformat(item["modified"]) if item.get("modified") else datetime.utcnow())
            db.add(asset)
            count += 1
    db.commit()
    return {"message": f"تم استيراد {count} أصل", "count": count}

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    return {"totalAssets": db.query(Asset).count(),
            "totalImages": db.query(Asset).filter(Asset.type == "image").count(),
            "totalTemplates": db.query(Asset).filter(Asset.type == "template").count(),
            "totalPages": db.query(Asset).filter(Asset.type == "page").count()}

@app.get("/api/collections")
def get_collections(db: Session = Depends(get_db)):
    collections = [
        {"id": "images", "label": "مكتبة الصور", "labelEn": "Image Library", "icon": "image"},
        {"id": "templates", "label": "قوالب HTML", "labelEn": "HTML Templates", "icon": "code"},
        {"id": "pages", "label": "صفحات مولّدة", "labelEn": "Generated Pages", "icon": "globe"},
    ]
    result = []
    for col in collections:
        items = db.query(Asset).filter(Asset.type == col["id"]).all()
        col["count"] = len(items)
        col["items"] = [item.to_dict() for item in items]
        result.append(col)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
