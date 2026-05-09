#!/usr/bin/env python3
import json, os
from pathlib import Path
from datetime import datetime

FLUX_PATHS = [
    Path.home() / "Desktop" / "real_flux_images",
    Path.home() / "Desktop" / "Flux Images",
    Path.home() / "Desktop" / "Flux_Complete_Library",
]

TEMPLATE_PATHS = [
    Path.home() / "jonjon-lab" / "html-templates" / "landing",
    Path.home() / "jonjon-lab" / "html-templates" / "razen-landing-pages",
]

GENERATED_PATHS = [
    Path.home() / "Desktop" / "HTML_Outputs",
]

OUTPUT_PATH = Path.home() / "jonjon-lab" / "_factory" / "data" / "assets.json"

def format_size(s):
    for u in ['B','KB','MB','GB']:
        if s < 1024: return f"{s:.1f} {u}"
        s /= 1024
    return f"{s:.1f} TB"

def scan_images():
    images = []
    for flux_path in FLUX_PATHS:
        if not flux_path.exists(): continue
        print(f"📁 مسح: {flux_path.name}")
        count_before = len(images)
        for root, dirs, files in os.walk(flux_path):
            for file in files:
                if file.lower().endswith(('.png','.jpg','.jpeg','.gif','.webp','.svg')):
                    fp = Path(root)/file
                    cat = Path(root).name if Path(root) != flux_path else "uncategorized"
                    images.append({"id":f"img_{len(images):04d}","name":file,"path":str(fp),"relativePath":str(fp.relative_to(Path.home())),"type":"image","category":cat,"source":flux_path.name,"size":format_size(fp.stat().st_size),"sizeBytes":fp.stat().st_size,"extension":fp.suffix.lower(),"modified":datetime.fromtimestamp(fp.stat().st_mtime).isoformat()})
        print(f"   ✅ +{len(images)-count_before} صورة")
    return images

def scan_templates():
    templates = []
    for tpl_path in TEMPLATE_PATHS:
        if not tpl_path.exists(): continue
        print(f"📁 مسح القوالب: {tpl_path.name}")
        for item in sorted(tpl_path.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                flist = [{"name":f.name,"extension":f.suffix.lower()} for f in item.rglob("*") if f.is_file()]
                templates.append({"id":f"tpl_{len(templates):04d}","name":item.name,"path":str(item),"relativePath":str(item.relative_to(Path.home())),"type":"template","category":tpl_path.name,"source":tpl_path.name,"filesCount":len(flist),"files":flist[:10],"totalFiles":len(flist)})
    return templates

def scan_generated():
    pages = []
    for gen_path in GENERATED_PATHS:
        if not gen_path.exists(): continue
        print(f"📁 مسح الصفحات المولّدة: {gen_path.name}")
        for item in sorted(gen_path.iterdir()):
            if item.is_file() and item.suffix.lower() in ['.html','.htm']:
                pages.append({"id":f"gen_{len(pages):04d}","name":item.name,"path":str(item),"relativePath":str(item.relative_to(Path.home())),"type":"page","category":"generated","source":"HTML_Outputs","size":format_size(item.stat().st_size),"sizeBytes":item.stat().st_size,"extension":item.suffix.lower(),"modified":datetime.fromtimestamp(item.stat().st_mtime).isoformat()})
    print(f"   ✅ +{len(pages)} صفحة")
    return pages

def main():
    print("🔍 بدء مسح الأصول...")
    images = scan_images()
    print(f"\n📸 إجمالي الصور: {len(images)}")
    templates = scan_templates()
    print(f"📄 إجمالي القوالب: {len(templates)}")
    pages = scan_generated()
    print(f"🌐 إجمالي الصفحات: {len(pages)}")
    
    assets = {
        "metadata":{"scannedAt":datetime.now().isoformat(),"version":"4.0"},
        "collections":[
            {"id":"images","label":"مكتبة الصور","labelEn":"Image Library","icon":"image","count":len(images),"items":images},
            {"id":"templates","label":"قوالب HTML","labelEn":"HTML Templates","icon":"code","count":len(templates),"items":templates},
            {"id":"pages","label":"صفحات مولّدة","labelEn":"Generated Pages","icon":"globe","count":len(pages),"items":pages}
        ],
        "summary":{"totalImages":len(images),"totalTemplates":len(templates),"totalPages":len(pages),"totalAssets":len(images)+len(templates)+len(pages)}
    }
    
    OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True)
    with open(OUTPUT_PATH,'w',encoding='utf-8') as f:
        json.dump(assets,f,ensure_ascii=False,indent=2)
    
    print(f"\n✅ تم الحفظ: {OUTPUT_PATH}")
    print(f"📊 إجمالي الأصول: {assets['summary']['totalAssets']}")

if __name__=="__main__":
    main()
