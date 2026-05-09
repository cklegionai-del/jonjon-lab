import asyncio
import os
import json
from playwright.async_api import async_playwright

OUTPUT_DIR = os.path.expanduser("~/jonjon-lab/agents/awwwards/library")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CATEGORIES = {
    "real-estate-architecture": {
        "label": "Real Estate & Architecture",
        "url": "https://www.awwwards.com/websites/architecture/",
        "emoji": "🏛️"
    },
    "restaurant-hotel": {
        "label": "Restaurant & Hotel",
        "url": "https://www.awwwards.com/websites/restaurant/",
        "emoji": "🍽️"
    },
    "fashion-luxury": {
        "label": "Fashion & Luxury",
        "url": "https://www.awwwards.com/websites/fashion/",
        "emoji": "💎"
    },
    "portfolio-agency": {
        "label": "Portfolio & Agency",
        "url": "https://www.awwwards.com/websites/portfolio/",
        "emoji": "🎨"
    },
    "ecommerce": {
        "label": "E-commerce",
        "url": "https://www.awwwards.com/websites/e-commerce/",
        "emoji": "🛍️"
    },
    "saas-tech": {
        "label": "SaaS & Tech",
        "url": "https://www.awwwards.com/websites/saas/",
        "emoji": "🚀"
    },
}

SITES_PER_CATEGORY = 10

async def scrape_category(page, cat_id, cat_info):
    print(f"\n{cat_info['emoji']} {cat_info['label']}...")
    cat_dir = os.path.join(OUTPUT_DIR, cat_id)
    os.makedirs(cat_dir, exist_ok=True)

    sites = []

    try:
        await page.goto(cat_info['url'], wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        cards = await page.query_selector_all(".card-site")
        print(f"  وجدت {len(cards)} موقع")

        for i, card in enumerate(cards[:SITES_PER_CATEGORY]):
            try:
                # اسم الموقع
                name_el = await card.query_selector(".card-site__info h2, .card-site__info h3, .card-site__info strong")
                name = await name_el.inner_text() if name_el else f"site_{i+1}"
                name = name.strip().replace("/", "-")[:50]

                # الرابط
                link_el = await card.query_selector("a.card-site__link, a")
                href = await link_el.get_attribute("href") if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://www.awwwards.com" + href

                # screenshot للـ card
                screenshot_path = os.path.join(cat_dir, f"{i+1:02d}_{name}.png")
                await card.screenshot(path=screenshot_path)

                sites.append({
                    "rank": i + 1,
                    "name": name,
                    "awwwards_url": href,
                    "screenshot": screenshot_path,
                    "category": cat_info['label'],
                    "category_id": cat_id
                })
                print(f"  ✅ {i+1}. {name}")

            except Exception as e:
                print(f"  ⚠️ site {i+1}: {e}")
                continue

    except Exception as e:
        print(f"  ❌ Error: {e}")

    meta_path = os.path.join(cat_dir, "sites.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)

    return sites

async def main():
    print("🚀 Awwwards Library Scraper")
    print("=" * 50)

    all_sites = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        for cat_id, cat_info in CATEGORIES.items():
            sites = await scrape_category(page, cat_id, cat_info)
            all_sites[cat_id] = sites
            await asyncio.sleep(2)

        await browser.close()

    master_path = os.path.join(OUTPUT_DIR, "master.json")
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(all_sites, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in all_sites.values())
    print(f"\n🎉 انتهى! {total} موقع في {len(all_sites)} categories")
    print(f"📁 المكتبة: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
