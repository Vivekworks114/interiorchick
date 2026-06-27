#!/usr/bin/env python3
"""Fetch WordPress content from interiorchick.nl and generate Astro content files."""

from __future__ import annotations

import html as html_lib
import json
import re
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://interiorchick.nl"
PUBLIC = ROOT / "public/images"
BLOG_DIR = ROOT / "src/content/blog"
PAGES_DIR = ROOT / "src/content/pages"
DATA_DIR = ROOT / "src/data"

SKIP_PAGE_SLUGS = {"home", "sample-page", "sample-page-2", "zb_mp_product"}
DEFAULT_IMAGE = "/images/2023/06/digitale-wekker.jpeg"

PRODUCT_IMAGES = {
    "beste-digitale-wekker": "/images/2023/06/digitale-wekker.jpeg",
    "beste-rieten-wasmand": "/images/2023/06/rieten-wasmand.jpeg",
    "beste-douchekop-met-slang": "/images/2023/06/douchekop.jpeg",
    "beste-zwevend-tv-meubel": "/images/2023/06/zwevend-tv-meubel.jpeg",
    "beste-droogtoren": "/images/2023/06/droogtoren.jpeg",
    "beste-grote-zitzak": "/images/2025/12/zitzak-2-1024x682.jpg",
    "beste-tv": "/images/2023/06/tv.jpeg",
    "beste-poef-met-opbergruimte": "/images/2023/06/poef-met-opbergruimte.jpeg",
    "beste-hangstoel-binnen": "/images/2023/06/hangstoel-binnen-1.jpeg",
    "beste-plafond-ventilator": "/images/2023/06/plafond-ventilator.jpeg",
    "beste-matras-120x200": "/images/2023/06/matras-120-x-200.jpeg",
    "beste-satijnen-kussensloop": "/images/2023/06/satijnen-kussensloop.jpeg",
}


def fetch_json(url: str) -> list | dict:
    result = subprocess.run(
        ["curl", "-sfL", "--max-time", "60", url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch {url}: {result.stderr}")
    return json.loads(result.stdout)


def upload_to_local(url: str) -> str:
    if not url:
        return url
    clean = url.split("?")[0]
    if "/wp-content/uploads/" in clean:
        rel = clean.split("/wp-content/uploads/", 1)[1]
        return f"/images/{rel}"
    return clean


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def rewrite_content(content: str, url_map: dict[str, str]) -> str:
    if not content:
        return ""

    def replace_url(match: re.Match) -> str:
        url = match.group(0)
        local = url_map.get(url) or url_map.get(url.split("?")[0])
        if local:
            return local
        if "/wp-content/uploads/" in url:
            local_path = upload_to_local(url)
            url_map[url] = local_path
            url_map[url.split("?")[0]] = local_path
            return local_path
        return url

    content = re.sub(
        rf"https?://(?:www\.)?interiorchick\.nl/wp-content/uploads/[^\s\"'<>]+",
        replace_url,
        content,
    )
    content = re.sub(
        rf"{re.escape(SITE)}/(?P<slug>[a-z0-9\-_/]+)/?",
        r"/\g<slug>/",
        content,
    )
    return content


def extract_first_image(content: str) -> str | None:
    for pattern in [
        r'src="(/images/[^"]+)"',
        r'src="https?://[^"]+/wp-content/uploads/([^"]+)"',
    ]:
        match = re.search(pattern, content or "")
        if match:
            src = match.group(1)
            if src.startswith("/images/"):
                return src
            return f"/images/{src}"
    return None


def download_image(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["curl", "-sfL", "--max-time", "45", url, "-o", str(dest)],
        capture_output=True,
    )
    return result.returncode == 0 and dest.exists() and dest.stat().st_size > 0


def download_images(urls: set[str]) -> None:
    tasks = []
    for url in sorted(urls):
        if not url or url.startswith("data:"):
            continue
        local = upload_to_local(url)
        if not local.startswith("/images/"):
            continue
        dest = ROOT / "public" / local.lstrip("/")
        tasks.append((url.split("?")[0], dest))

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(download_image, u, d): (u, d) for u, d in tasks}
        done = 0
        for future in as_completed(futures):
            done += 1
            if done % 20 == 0:
                print(f"  Downloaded {done}/{len(tasks)} images...")


def fetch_all_posts() -> list[dict]:
    posts = []
    page = 1
    while True:
        batch = fetch_json(f"{SITE}/wp-json/wp/v2/posts?per_page=100&page={page}")
        if not batch:
            break
        posts.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return posts


def fetch_all_pages() -> list[dict]:
    return fetch_json(f"{SITE}/wp-json/wp/v2/pages?per_page=100")


def fetch_products() -> list[str]:
    result = subprocess.run(
        ["curl", "-sfL", "--max-time", "60", f"{SITE}/zb_mp-sitemap.xml"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [loc.split("/")[-2] for loc in re.findall(r"<loc>([^<]+)</loc>", result.stdout)]


def get_media_url(media_id: int, cache: dict) -> str | None:
    if not media_id:
        return None
    if media_id in cache:
        return cache[media_id]
    try:
        data = fetch_json(f"{SITE}/wp-json/wp/v2/media/{media_id}")
        url = data.get("source_url")
        cache[media_id] = url
        return url
    except Exception:
        cache[media_id] = None
        return None


def write_blog_post(post: dict, media_cache: dict, url_map: dict) -> str | None:
    slug = post["slug"]
    title = html_lib.unescape(strip_html(post["title"]["rendered"]))
    content = post["content"]["rendered"]
    excerpt = strip_html(post["excerpt"]["rendered"])[:300]
    pub_date = post["date"][:10]

    featured = None
    media_id = post.get("featured_media", 0)
    if media_id:
        media_url = get_media_url(media_id, media_cache)
        if media_url:
            featured = upload_to_local(media_url)

    if not featured:
        featured = extract_first_image(content) or DEFAULT_IMAGE

    body = rewrite_content(content, url_map)
    frontmatter = f"""---
title: {yaml_quote(title)}
description: {yaml_quote(excerpt)}
pubDate: {pub_date}
featuredImage: {yaml_quote(featured)}
imageAlt: {yaml_quote(title)}
---

"""
    html_dir = ROOT / "src/data/page-html"
    html_dir.mkdir(parents=True, exist_ok=True)
    (html_dir / f"{slug}.html").write_text(body or f"<p>{excerpt}</p>", encoding="utf-8")
    path = BLOG_DIR / f"{slug}.mdx"
    path.write_text(frontmatter, encoding="utf-8")
    return slug


def write_page(page: dict, media_cache: dict, url_map: dict, is_product: bool = False) -> str | None:
    slug = page["slug"]
    if slug in SKIP_PAGE_SLUGS:
        return None

    title = html_lib.unescape(strip_html(page["title"]["rendered"]))
    content = page["content"]["rendered"]
    excerpt = strip_html(page["excerpt"]["rendered"])[:300] or f"Lees meer over {title} op InteriorChick.nl."

    featured = PRODUCT_IMAGES.get(slug)
    if not featured:
        media_id = page.get("featured_media", 0)
        if media_id:
            media_url = get_media_url(media_id, media_cache)
            if media_url:
                featured = upload_to_local(media_url)
    if not featured:
        featured = extract_first_image(content) or DEFAULT_IMAGE

    body = rewrite_content(content, url_map)
    page_type = 'product' if is_product or slug.startswith("beste-") else 'page'

    frontmatter = f"""---
title: {yaml_quote(title)}
description: {yaml_quote(excerpt)}
featuredImage: {yaml_quote(featured)}
pageType: {yaml_quote(page_type)}
---

"""
    html_dir = ROOT / "src/data/page-html"
    html_dir.mkdir(parents=True, exist_ok=True)
    (html_dir / f"{slug}.html").write_text(body or f"<p>{excerpt}</p>", encoding="utf-8")
    path = PAGES_DIR / f"{slug}.mdx"
    path.write_text(frontmatter, encoding="utf-8")
    return slug


def create_product_fallback(slug: str) -> str:
    name = slug.replace("beste-", "").replace("-", " ")
    title = f"Beste {name}"
    featured = PRODUCT_IMAGES.get(slug, DEFAULT_IMAGE)
    description = f"Ontdek de beste {name} opties op InteriorChick.nl. Vergelijk top producten en maak de juiste keuze voor jouw interieur."

    frontmatter = f"""---
title: {yaml_quote(title)}
description: {yaml_quote(description)}
featuredImage: {yaml_quote(featured)}
pageType: "product"
---

"""
    html_dir = ROOT / "src/data/page-html"
    html_dir.mkdir(parents=True, exist_ok=True)
    html_body = f"<p>Welkom op InteriorChick.nl. In dit overzicht delen we onze tips en ervaringen over {name}. Bekijk regelmatig onze site voor de nieuwste productvergelijkingen en interieurtips.</p>"
    path = PAGES_DIR / f"{slug}.mdx"
    if not path.exists():
        (html_dir / f"{slug}.html").write_text(html_body, encoding="utf-8")
        path.write_text(frontmatter, encoding="utf-8")
    return slug


def collect_image_urls(posts: list, pages: list) -> set[str]:
    urls: set[str] = set()
    pattern = re.compile(rf"https?://(?:www\.)?interiorchick\.nl/wp-content/uploads/[^\s\"'<>]+")

    static_images = [
        f"{SITE}/wp-content/uploads/2023/01/Group-8031.jpg",
        f"{SITE}/wp-content/uploads/2023/01/Group-8131.jpg",
        f"{SITE}/wp-content/uploads/2023/01/InteriorChick.nl_-1.svg",
        f"{SITE}/wp-content/uploads/2023/01/InteriorChick.nl1_.svg",
        f"{SITE}/wp-content/uploads/2023/01/icon-park-outline_plug-one.svg",
        f"{SITE}/wp-content/uploads/2023/01/icon-park-outline_sofa.svg",
        f"{SITE}/wp-content/uploads/2023/01/icon-park-outline_four-leaves.svg",
        f"{SITE}/wp-content/uploads/2023/01/icon-park-outline_color-filter.svg",
        f"{SITE}/wp-content/uploads/2023/01/icon-park-outline_great-wall.svg",
        f"{SITE}/wp-content/uploads/2023/01/icon-park-outline_floor-tile.svg",
    ]
    for img in static_images:
        urls.add(img)
    for img in PRODUCT_IMAGES.values():
        urls.add(f"{SITE}/wp-content/uploads/{img.replace('/images/', '')}")

    for item in posts + pages:
        content = item.get("content", {}).get("rendered", "")
        urls.update(pattern.findall(content))

    # Try douchekop full image
    urls.add(f"{SITE}/wp-content/uploads/2023/06/douchekop.jpeg")

    return urls


def main() -> None:
    print("Fetching WordPress content from interiorchick.nl...")
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    posts = fetch_all_posts()
    pages = fetch_all_pages()
    product_slugs = fetch_products()
    print(f"  Posts: {len(posts)}, Pages: {len(pages)}, Products: {len(product_slugs)}")

    image_urls = collect_image_urls(posts, pages)
    print(f"Downloading {len(image_urls)} images...")
    download_images(image_urls)

    url_map: dict[str, str] = {}
    media_cache: dict[int, str | None] = {}

    blog_slugs = []
    for post in posts:
        slug = write_blog_post(post, media_cache, url_map)
        if slug:
            blog_slugs.append(slug)

    page_slugs = []
    existing_page_slugs = {p["slug"] for p in pages}
    for page in pages:
        slug = write_page(page, media_cache, url_map)
        if slug:
            page_slugs.append(slug)

    for slug in product_slugs:
        if slug not in existing_page_slugs:
            create_product_fallback(slug)
            page_slugs.append(slug)

    all_slugs = sorted(set(blog_slugs + page_slugs + product_slugs + [
        "contact", "over-ons", "sitemap", "laatste-blogs",
        "slaapkamer", "interieur", "wasruimte", "keuken", "terras", "veiligheid", "melders",
    ]))

    (DATA_DIR / "slugs.json").write_text(json.dumps(all_slugs, indent=2), encoding="utf-8")
    (DATA_DIR / "blog-posts.json").write_text(
        json.dumps([{"slug": s, "title": s} for s in blog_slugs[:20]], indent=2),
        encoding="utf-8",
    )

    summary = {
        "posts": len(blog_slugs),
        "pages": len(page_slugs),
        "products": len(product_slugs),
        "images": len(image_urls),
    }
    print("Done:", json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
